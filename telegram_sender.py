"""
telegram_sender.py
Part 1
"""

import os
import time
import requests


# ==========================================================
# Environment
# ==========================================================

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASE_URL = (
    f"https://api.telegram.org/bot{BOT_TOKEN}"
    if BOT_TOKEN
    else ""
)

DEFAULT_TIMEOUT = 30


# ==========================================================
# Validation
# ==========================================================

def validate_environment():

    if not BOT_TOKEN:
        raise ValueError(
            "GitHub Secret 'TELEGRAM_TOKEN' not found."
        )

    if not CHAT_ID:
        raise ValueError(
            "GitHub Secret 'TELEGRAM_CHAT_ID' not found."
        )


# ==========================================================
# Telegram Request
# ==========================================================

def telegram_post(
    method,
    payload,
):

    validate_environment()

    url = f"{BASE_URL}/{method}"

    response = requests.post(
        url,
        json=payload,
        timeout=DEFAULT_TIMEOUT,
    )

    print("=" * 60)
    print("Telegram API")
    print("Method :", method)
    print("Status :", response.status_code)
    print("Body   :", response.text)
    print("=" * 60)

    response.raise_for_status()

    return response.json()


# ==========================================================
# Send One Message
# ==========================================================

def send_telegram_message(
    message,
    parse_mode=None,
):

    payload = {

        "chat_id": CHAT_ID,

        "text": message,

        "disable_web_page_preview": True,

    }

    if parse_mode:

        payload["parse_mode"] = parse_mode

    return telegram_post(
        "sendMessage",
        payload,
    )


# ==========================================================
# Send Multiple Messages
# ==========================================================

def send_telegram_messages(
    messages,
):

    if not messages:
        return

    results = []

    for message in messages:

        result = send_telegram_message(
            message
        )

        results.append(result)

        time.sleep(1)

    return results

# ==========================================================
# Send Photo
# ==========================================================

def send_telegram_photo(
    photo_url,
    caption="",
):

    payload = {

        "chat_id": CHAT_ID,

        "photo": photo_url,

        "caption": caption,

    }

    return telegram_post(
        "sendPhoto",
        payload,
    )


# ==========================================================
# Send Document
# ==========================================================

def send_telegram_document(
    document_url,
    caption="",
):

    payload = {

        "chat_id": CHAT_ID,

        "document": document_url,

        "caption": caption,

    }

    return telegram_post(
        "sendDocument",
        payload,
    )


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    try:

        send_telegram_message(
            "✅ Telegram Test Success!"
        )

        print()
        print("Telegram Send : OK")

    except Exception as e:

        print()
        print("Telegram Send : FAIL")
        print(e)


# ==========================================================
# End of telegram_sender.py
# ==========================================================
