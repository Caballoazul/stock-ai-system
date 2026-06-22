import os
import requests

def send_telegram(message):

    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    # 🔍 디버깅 (가장 중요)
    print("TOKEN:", token)
    print("CHAT_ID:", chat_id)

    # ❗ 안전장치
    if not token or not chat_id:
        print("❌ TELEGRAM 환경변수 없음 (GitHub Secrets 확인 필요)")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        response = requests.post(url, data=payload, timeout=10)

        print("Telegram response:", response.text)

        if response.status_code != 200:
            print("❌ Telegram 전송 실패")

        return response.text

    except Exception as e:
        print("❌ Telegram 예외 발생:", str(e))
