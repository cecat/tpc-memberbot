#!/usr/bin/env python3
"""main.py

Entry point and orchestrator for the TPC MemberBot system.

Logging behaviour
-----------------
* Always write **all** log records (DEBUG+) to *memberbot.log* in the repo root.
* If ``-v`` / ``--verbose`` is passed, **also** emit logs to the console.

Duplicate‑email handling
-----------------------
Within a single run we skip rows whose email address (case‑insensitive) has
already been processed.  That means a CSV containing duplicate addresses will
only perform each action once per invocation.
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Set

from agents import (
    request_handler,
    domain_checker,
    slack_inviter,
    mailman_agent,
    spreadsheet_updater,
    email_notifier,
)

###############################################################################
# Logging helpers
###############################################################################

def _setup_logging(verbose: bool = False) -> None:
    """Configure root logger with file + optional stream handler."""
    log_path = Path("memberbot.log")

    # File handler (always on)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)

    # Optional console handler
    handlers = [file_handler]
    if verbose:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(file_formatter)
        handlers.append(stream_handler)

    logging.basicConfig(level=logging.DEBUG, handlers=handlers, force=True)


logger = logging.getLogger(__name__)

###############################################################################
# Main workflow
###############################################################################

def main() -> None:
    """Top‑level orchestration loop."""
    parser = argparse.ArgumentParser(description="TPC MemberBot orchestrator")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="also log to the console"
    )
    args = parser.parse_args()

    _setup_logging(args.verbose)
    logger.info("🔄  TPC MemberBot starting…")

    new_requests = request_handler.get_new_requests()
    logger.info("📥  %d new request(s) found", len(new_requests))

    seen: Set[str] = set()  # deduplicate by email within this run

    for req in new_requests:
        email = req["email"].strip().lower()
        if email in seen:
            logger.debug("⏩  Skipping duplicate email %s", email)
            continue
        seen.add(email)

        logger.info("→ Processing %s", email)

        if not domain_checker.is_valid_email(email):
            email_notifier.request_institutional_email(req)
            spreadsheet_updater.update_tracker(req, slack_invited=False)
            continue

        if domain_checker.is_whitelisted(email):
            slack_inviter.send_invite(req)

        mailman_agent.add_to_lists(req)
        spreadsheet_updater.update_all(req, slack_invited=True)

    logger.info("✅  Processing complete; processed %d unique addresses", len(seen))


if __name__ == "__main__":
    main()

