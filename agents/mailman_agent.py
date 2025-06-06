#!/usr/bin/env python3
"""
mailman_agent.py

Adds users to Mailman (Mailman 2) mailing lists by emulating the
web-form POSTs.  Currently a stub that only logs the action.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def add_to_lists(req: dict) -> None:
    """
    Subscribe the requestor to the appropriate lists.

    Args
    ----
    req : dict
        Must contain at least 'email'.
    """
    # TODO: Implement HTTP POST to list admin pages.
    logger.info("📧  Added %s to mailing lists", req["email"])

