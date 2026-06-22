# =====================================================
# telegram_sender.py
# Telegram Sender Module
# =====================================================

import os
import requests


# Telegram 메시지 최대 길이
MAX_MESSAGE_LENGTH = 4000


def send_telegram(message):

    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    print("=" * 60)
    print("Telegram Sender")
    print("=" * 60)

    # -------------------------------------------------
    # 환경변수 확인
    # -------------------------------------------------

    if not token:
        print("❌ TELEGRAM_TOKEN 없음")
        return False

    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID 없음")
        return False

    print("✔ TOKEN 확인")
    print("✔ CHAT_ID 확인")

    # -------------------------------------------------
    # Telegram 4096자 제한 대응
    # -------------------------------------------------

    chunks = []

    if len(message) <= MAX_MESSAGE_LENGTH:

        chunks.append(message)

    else:

        for i in range(
            0,
            len(message),
            MAX_MESSAGE_LENGTH
        ):
            chunks.append(
                message[
                    i:i + MAX_MESSAGE_LENGTH
                ]
            )

    print(
        f"메시지 분할 수 : {len(chunks)}"
    )

    # -------------------------------------------------
    # 전송
    # -------------------------------------------------

    url = (
        f"https://api.telegram.org/"
        f"bot{token}/sendMessage"
    )

    success_count = 0

    for idx, chunk in enumerate(
        chunks,
        start=1
    ):

        payload = {
            "chat_id": chat_id,
            "text": chunk
        }

        try:

            response = requests.post(
                url,
                data=payload,
                timeout=15
            )

            print(
                f"[{idx}/{len(chunks)}]"
            )

            print(
                f"Status : "
                f"{response.status_code}"
            )

            print(
                response.text[:200]
            )

            if response.status_code == 200:

                result = response.json()

                if result.get("ok"):

                    success_count += 1

                    print(
                        "✔ 전송 성공"
                    )

                else:

                    print(
                        "❌ Telegram 응답 오류"
                    )

            else:

                print(
                    "❌ HTTP 오류"
                )

        except Exception as e:

            print(
                f"❌ Exception : {e}"
            )

    # -------------------------------------------------
    # 결과
    # -------------------------------------------------

    print("=" * 60)

    print(
        f"전송 성공 : "
        f"{success_count}"
        f"/{len(chunks)}"
    )

    print("=" * 60)

    return (
        success_count ==
        len(chunks)
    )


# =====================================================
# 단독 실행 테스트
# =====================================================

if __name__ == "__main__":

    test_message = """
🚀 Telegram Test

Semiconductor Quant Dashboard

Micron
Samsung
SK Hynix

Transmission Test
"""

    send_telegram(
        test_message
    )
