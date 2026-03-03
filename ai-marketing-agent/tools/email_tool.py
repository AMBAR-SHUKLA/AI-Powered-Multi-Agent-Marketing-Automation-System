"""
Email outreach tool — sends emails via SMTP.
Configure SMTP credentials in .env to enable live sending.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.config import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


def send_email(to: str, subject: str, body: str, html: bool = False) -> dict:
    """
    Send an email via SMTP.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Email body (plain text or HTML).
        html: If True, sends as HTML; otherwise plain text.

    Returns:
        {"status": "sent"} on success, {"status": "error", "error": str} on failure.
    """
    if not settings.smtp_user or not settings.smtp_pass:
        logger.warning("[EmailTool] SMTP credentials not configured. Skipping send.")
        return {"status": "skipped", "reason": "SMTP not configured"}

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = settings.smtp_user
        msg["To"] = to
        msg["Subject"] = subject

        mime_type = "html" if html else "plain"
        msg.attach(MIMEText(body, mime_type))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_pass)
            server.sendmail(settings.smtp_user, to, msg.as_string())

        logger.info(f"[EmailTool] Email sent to {to} — subject: {subject}")
        return {"status": "sent"}

    except Exception as e:
        logger.error(f"[EmailTool] Failed to send email to {to}: {e}")
        return {"status": "error", "error": str(e)}
