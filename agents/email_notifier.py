#!/usr/bin/env python3
"""
email_notifier.py

Sends follow-up emails when a personal/anonymous address is submitted,
requesting an institutional email instead.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def request_institutional_email(req: dict) -> None:
    """
    Ask the user to resubmit with an institutional address.

    Args
    ----
    req : dict
        Must contain at least 'email'.
    """
    # TODO: Real email send (SMTP or third-party)
    logger.info("📮  Requested institutional email from %s", req["email"])

