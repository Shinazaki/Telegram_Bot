import asyncio
import random
import smtplib
from email.message import EmailMessage

from app.config import (
    SMTP_FROM,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USE_SSL,
    SMTP_USER,
)


def generate_verification_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def _send_code_sync(recipient: str, code: str) -> None:
    if not SMTP_USER or not SMTP_PASSWORD:
        raise RuntimeError("SMTP credentials are not configured")

    sender_email = SMTP_USER.strip()
    configured_from = SMTP_FROM.strip()
    if configured_from and configured_from.lower() == sender_email.lower():
        sender_email = configured_from

    message = EmailMessage()
    message["Subject"] = "Код подтверждения для Telegram-бота"
    message["From"] = sender_email
    message["To"] = recipient
    message.set_content(
        "Ваш код подтверждения для входа в бота: "
        f"{code}. Код действует ограниченное время."
    )

    if SMTP_USE_SSL:
        smtp = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15)
        try:
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.send_message(message)
        finally:
            smtp.close()
        return

    smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
    try:
        smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.send_message(message)
    finally:
        smtp.close()


async def send_verification_code(recipient: str, code: str) -> None:
    await asyncio.to_thread(_send_code_sync, recipient, code)
