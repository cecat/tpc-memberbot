#!/usr/bin/env python3
"""
main.py

Entry point and orchestrator for the TPC MemberBot system.

Usage
-----
$ ./main.py          # normal run (INFO logging)
$ ./main.py -v       # verbose run (DEBUG logging)

Pipeline
--------
1. Pull new Ninja-Forms submissions (request_handler)
2. Validate email & whitelist status (domain_checker)
3. Ask for institutional email if needed (email_notifier)
4. Invite eligible users to Slack (slack_inviter)
5. Subscribe users to Mailman lists (mailman_agent)
6. Update bookkeeping spreadsheets (spreadsheet_updater)
"""
from __future__ import annotations

import argparse
import logging

from agents import (
    request_handler,
    domain_checker,
    slack_inviter,
    mailman_agent,
    spreadsheet_updater,
    email_notifier,
)


def _setup_logging(verbose: bool = False) -> None:
    """Configure root-level logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


logger = logging.getLogger(__name__)


def main() -> None:
    """Main orchestration loop."""
    parser = argparse.ArgumentParser(description="TPC MemberBot orchestrator")
    parser.add_argument("-v", "--verbose", action="store_true", help="enable DEBUG logging")
    args = parser.parse_args()

    _setup_logging(args.verbose)
    logger.info("🔄  TPC MemberBot starting…")

    new_requests = request_handler.get_new_requests()
    logger.info("📥  %d new request(s) found", len(new_requests))

    for req in new_requests:
        logger.info("→ Processing %s", req["email"])

        if not domain_checker.is_valid_email(req["email"]):
            email_notifier.request_institutional_email(req)
            spreadsheet_updater.update_tracker(req, slack_invited=False)
            continue

        if domain_checker.is_whitelisted(req["email"]):
            slack_inviter.send_invite(req)

        mailman_agent.add_to_lists(req)
        spreadsheet_updater.update_all(req, slack_invited=True)

    logger.info("✅  Processing complete.")


if __name__ == "__main__":
    main()

