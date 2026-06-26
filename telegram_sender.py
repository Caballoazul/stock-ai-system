"""
telegram_sender.py
"""

import os
import requests


# ==========================================================
# Environment
# ==========================================================

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# ==========================================================
# Telegram Send
# ==========================================================

def send_telegram_message(message):

    if not BOT_TOKEN:
        raise ValueError(
            "GitHub Secret 'TELEGRAM_BOT_TOKEN' not found."
        )

    if not CHAT_ID:
        raise ValueError(
            "GitHub Secret 'TELEGRAM_CHAT_ID' not found."
        )

    url = (
        f"https://api.telegram.org/bot"
        f"{BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": True,
    }

    response = requests.post(
        url,
        json=payload,
        timeout=30,
    )

    print("=" * 60)
    print("Telegram API")
    print("Status :", response.status_code)
    print("Body   :", response.text)
    print("=" * 60)

    response.raise_for_status()

    return response.json()


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    send_telegram_message(
        "Telegram Test Success!"
    )
