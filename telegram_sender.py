"""
telegram_sender.py
"""

import os
import requests


# ==========================================================
# Environment
# ==========================================================

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# ==========================================================
# Send Telegram
# ==========================================================

def send_telegram_message(message):

    if not BOT_TOKEN:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN not found."
        )

    if not CHAT_ID:
        raise ValueError(
            "TELEGRAM_CHAT_ID not found."
        )

    url = (
        f"https://api.telegram.org/bot"
        f"{BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    response = requests.post(
        url,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


# ==========================================================
# Send Markdown
# ==========================================================

def send_markdown(message):

    url = (
        f"https://api.telegram.org/bot"
        f"{BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }

    response = requests.post(
        url,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


# ==========================================================
# End of telegram_sender.py
# ==========================================================
