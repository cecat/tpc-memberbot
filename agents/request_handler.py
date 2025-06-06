#!/usr/bin/env python3
"""
request_handler.py

Pulls and parses Ninja-Forms CSV exports, returning only rows
with IDs greater than the last one processed (deduplication).

Expected CSV columns
--------------------
ID, Your name, Email address, Organization or Affiliation
"""
from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

SUBMISSION_CSV = "data/nf-subs-1.csv"
STATE_FILE = "data/state.json"


def _load_last_processed_id() -> int:
    """Return the last processed ID (0 if the state file is missing)."""
    if not Path(STATE_FILE).exists():
        return 0
    return json.loads(Path(STATE_FILE).read_text()).get("last_id", 0)


def _save_last_processed_id(last_id: int) -> None:
    """Persist the most recent processed ID to disk."""
    Path(STATE_FILE).write_text(json.dumps({"last_id": last_id}))


def get_new_requests() -> List[Dict[str, str]]:
    """
    Parse the submission CSV and return a list of new, unprocessed requests.

    Returns
    -------
    List[Dict[str, str]]
        Each dict has keys: id, name, email, organization.
    """
    # map from our logical field -> header in the CSV
    COL = {
        "id": "#",
        "name": "Name (Last, First)",
        "email": "Email",
        "org": "Your Institution",
    }

    new_requests: List[Dict[str, str]] = []
    last_id = _load_last_processed_id()
    next_id = last_id

    with Path(SUBMISSION_CSV).open(newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row_no, row in enumerate(reader, start=1):
            raw_id = row.get(COL["id"], "").strip()
            try:
                row_id = int(raw_id)
            except ValueError:         # blank or non-numeric
                row_id = row_no        # fallback to monotonically increasing number

            if row_id > last_id:
                new_requests.append(
                    {
                        "id": row_id,
                        "name": row.get(COL["name"], "").strip(),
                        "email": row.get(COL["email"], "").strip(),
                        "organization": row.get(COL["org"], "").strip(),
                    }
                )
                next_id = max(next_id, row_id)

    _save_last_processed_id(next_id)
    logger.debug("Loaded %d new request(s)", len(new_requests))
    return new_requests

