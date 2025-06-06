#!/usr/bin/env python3
"""
slack_inviter.py

Sends Slack invitations to eligible email addresses.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def send_invite(req: dict) -> None:
    """
    Invite the user to Slack.  Actual API integration is TODO.

    Args
    ----
    req : dict
        Must contain at least an 'email' key.
    """
    # TODO: Integrate Slack admin API or bot workflow.
    logger.info("🚀  Slack invite sent to %s", req["email"])

