"""Transactional email delivery through SendGrid."""

import os
import re
from typing import Dict


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def send_recruiter_email(to_email: str, subject: str, body: str, reply_to: str = "") -> Dict:
    if not EMAIL_PATTERN.match(to_email.strip()):
        return {"success": False, "error": "A valid candidate email address is required"}
    api_key = os.getenv("SENDGRID_API_KEY", "").strip()
    from_email = os.getenv("SENDGRID_FROM_EMAIL", "").strip()
    from_name = os.getenv("SENDGRID_FROM_NAME", "Fydara").strip() or "Fydara"
    if not api_key or not from_email:
        return {"success": False, "error": "Email delivery is not configured. Set SENDGRID_API_KEY and SENDGRID_FROM_EMAIL."}
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, ReplyTo

        message = Mail(from_email=(from_email, from_name), to_emails=to_email, subject=subject, plain_text_content=body)
        if reply_to and EMAIL_PATTERN.match(reply_to):
            message.reply_to = ReplyTo(reply_to)
        response = SendGridAPIClient(api_key).send(message)
        if response.status_code not in {200, 201, 202}:
            return {"success": False, "error": f"Email provider returned status {response.status_code}"}
        return {"success": True, "status": "accepted", "provider_status": response.status_code, "message_id": response.headers.get("X-Message-Id", "")}
    except Exception as error:
        return {"success": False, "error": f"Email delivery failed: {error}"}


__all__ = ["send_recruiter_email"]
