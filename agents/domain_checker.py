#!/usr/bin/env python3
"""
domain_checker.py

Validates email structure and checks domains against a whitelist.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def is_valid_email(email: str) -> bool:
    """Return True if the address is not from a generic provider."""
    return "@" in email and not any(p in email for p in ("gmail.", "hotmail.", "yahoo."))


def is_whitelisted(email: str) -> bool:
    """True if the domain is in the approved whitelist."""
    return email.split("@")[-1].lower() in _load_whitelist()


def _load_whitelist() -> set[str]:
    """Load whitelisted domains (stubbed for now)."""
    # TODO: Replace with XLSX read.
    return {"anl.gov", "uchicago.edu", "lbl.gov"}

