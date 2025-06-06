#!/usr/bin/env python3
"""
spreadsheet_updater.py

Handles both the master workbook and the Slack-request tracker workbook.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def update_all(req: dict, slack_invited: bool) -> None:
    """Record the request in the *master* spreadsheet."""
    # TODO: Use openpyxl or Google Sheets API here.
    logger.info("📊  Master sheet updated for %s (slack_invited=%s)", req["email"], slack_invited)


def update_tracker(req: dict, slack_invited: bool) -> None:
    """Record the request in the Slack-tracker sheet."""
    # TODO: Use openpyxl or Google Sheets API here.
    logger.info("🗂  Tracker sheet updated for %s (slack_invited=%s)", req["email"], slack_invited)

