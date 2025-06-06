#!/usr/bin/env python3
"""
agents/domain_checker.py

• Validates e-mail structure (filters free-mail domains).
• Builds the whitelist *every run* as

    BASE  ∪  DOMAINS_FROM_TPC_MASTER  –  FREE_MAIL

Input files – searched in *data/*
--------------------------------
base_whitelist.csv   # one domain per line (maintained in Git)
TPC-MASTER.csv       # preferred master export
TPC-MASTER.xlsx      # fallback if CSV absent

If neither Master file exists, the dynamic part is empty and only the base list
is used.
"""
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Set

import pandas as pd

logger = logging.getLogger(__name__)

DATA_DIR = Path("data")
BASE_FILE   = DATA_DIR / "base_whitelist.csv"
MASTER_CSV  = DATA_DIR / "TPC-MASTER.csv"
MASTER_XLSX = DATA_DIR / "TPC-MASTER.xlsx"

FREE_MAIL = {
    "gmail.com", "googlemail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "live.com", "aol.com", "icloud.com", "protonmail.com", "gmx.com", "gmx.de",
    "pm.me",
}

###############################################################################
# Public helpers
###############################################################################

def is_valid_email(email: str) -> bool:
    """Return False if the domain is in *FREE_MAIL*."""
    return "@" in email and email.split("@")[1].lower() not in FREE_MAIL


def is_whitelisted(email: str) -> bool:
    return email.split("@")[-1].lower() in _build_whitelist()

###############################################################################
# Build whitelist (cached per run)
###############################################################################

@lru_cache(maxsize=1)
def _build_whitelist() -> Set[str]:
    base    = _load_base()
    dynamic = _extract_domains_from_master()

    wl = {d.lower().strip() for d in base | dynamic if d}
    logger.info(
        "Whitelist compiled: %d base + %d dynamic → %d total domains",
        len(base), len(dynamic), len(wl),
    )
    return wl


def _load_base() -> Set[str]:
    if not BASE_FILE.exists():
        logger.warning("Base whitelist %s missing – proceeding empty", BASE_FILE)
        return set()
    return {l.strip().lower() for l in BASE_FILE.read_text().splitlines() if l.strip()}


def _extract_domains_from_master() -> Set[str]:
    """Pull unique domains from whichever Master file exists (CSV > XLSX)."""
    path: Path | None = None
    if MASTER_CSV.exists():
        path = MASTER_CSV
        loader = pd.read_csv
    elif MASTER_XLSX.exists():
        path = MASTER_XLSX
        loader = lambda p: pd.read_excel(p, engine="openpyxl")
    else:
        logger.warning("No TPC-MASTER file found – dynamic whitelist empty")
        return set()

    try:
        df = loader(path)
        if "Email" not in df.columns:
            logger.warning("Column 'Email' missing in %s – dynamic part empty", path.name)
            return set()
        domains = {
            str(e).split("@")[1].lower().strip()
            for e in df["Email"].dropna()
            if "@" in str(e) and str(e).split("@")[1].lower().strip() not in FREE_MAIL
        }
        logger.debug("Dynamic whitelist: %d domains extracted from %s", len(domains), path.name)
        return domains
    except Exception as exc:  # pragma: no cover
        logger.error("Failed reading %s: %s", path, exc, exc_info=True)
        return set()

