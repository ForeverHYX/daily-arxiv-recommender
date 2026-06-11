"""SMTP delivery for recommendation digest emails."""

from __future__ import annotations

import argparse
from email.message import EmailMessage
import json
import os
from pathlib import Path
import smtplib

from paper_recommender.emailer import render_email_html


def build_email_message(subject: str, sender: str, receiver: str, html: str) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = receiver
    message.set_content(html, subtype="html")
    return message


def send_email_message(
    message: EmailMessage,
    smtp_host: str,
    smtp_port: int,
    username: str,
    password: str,
    use_ssl: bool = True,
) -> None:
    if use_ssl:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as smtp:
            smtp.login(username, password)
            smtp.send_message(message)
    else:
        with smtplib.SMTP(smtp_host, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(message)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Send recommendation digest email.")
    parser.add_argument("--recommendations", required=True, help="Recommendation JSON payload.")
    parser.add_argument("--subject", default=None, help="Email subject override.")
    args = parser.parse_args(argv)

    payload = json.loads(Path(args.recommendations).read_text(encoding="utf-8"))
    site_base_url = _required_env("SITE_BASE_URL")
    feedback_base_url = os.environ.get("FEEDBACK_BASE_URL", f"{site_base_url.rstrip('/')}/feedback.html")
    html = render_email_html(payload, site_base_url=site_base_url, feedback_base_url=feedback_base_url)

    sender = _required_env("EMAIL_SENDER")
    receiver = _required_env("EMAIL_RECEIVER")
    subject = args.subject or f"Daily arXiv Recommendations - {payload.get('run_date', '')}"
    message = build_email_message(subject=subject, sender=sender, receiver=receiver, html=html)

    smtp_host = _required_env("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "465"))
    username = os.environ.get("SMTP_USERNAME", sender)
    password = _required_env("SMTP_PASSWORD")
    use_ssl = os.environ.get("SMTP_USE_SSL", "true").lower() != "false"
    send_email_message(
        message,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        username=username,
        password=password,
        use_ssl=use_ssl,
    )
    print(f"Sent recommendation digest to {receiver}")
    return 0


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
