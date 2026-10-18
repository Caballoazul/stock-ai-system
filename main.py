"""Semiconductor reports: AM/PM Gmail, Telegram, Kako; NXT pending."""
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from market_intelligence import fetch_market, fetch_news
from insight_report import compose
from gmail_reader import fetch_recent_briefings
from briefing_integration import format_briefings
from gmail_sender import send_gmail_report
from telegram_sender import send_telegram_message
from kakao_sender import send_kakao_messages

KST = ZoneInfo("Asia/Seoul")
MODES = {"morning", "afternoon", "night"}


def resolve_mode():
    mode = os.getenv("REPORT_MODE", "").strip().lower()
    if mode not in MODES:
        raise ValueError("REPORT_MODE must be morning, afternoon, or night")
    return mode


def get_telegram_link(response):
    """Only public username/channel links can be built reliably here."""
    username = os.getenv("TELEGRAM_PUBLIC_USERNAME", "").strip().lstrip("@")
    result = response.get("result", {}) if isinstance(response, dict) else {}
    message_id = result.get("message_id")
    if username and message_id and username.replace("_", "").isalnum():
        return f"https://t.me/{username}/{message_id}"
    return None


def main():
    mode = resolve_mode()
    now = datetime.now(KST)
    print(f"Report mode: {mode}; KST: {now.isoformat()}")
    if mode == "night":
        print("NIGHT_NOT_READY: verified NXT 20:00 prices unavailable; no messages sent")
        return {"mode": mode, "status": "pending_nxt_source"}

    market = fetch_market()
    news, news_error = fetch_news()
    title, detailed, telegram_text = compose(mode, market, news, news_error)

    # The new integration changes only the detailed Gmail content.
    # Failure to read Gmail must not stop existing report delivery.
    try:
        briefings = fetch_recent_briefings(hours=24)
        print(f"GMAIL_BRIEFINGS_FOUND={len(briefings)}")
        detailed += format_briefings(briefings, now=now)
    except Exception as exc:
        print(f"GMAIL_BRIEFING_READ_FAILED={type(exc).__name__}")
        detailed += ("\n\n[삼성전자·SK하이닉스 뉴스 브리핑]\n"
                     "Gmail 브리핑을 읽지 못해 원본 뉴스 분석을 포함하지 않았습니다.")

    subject = f"[반도체보고서][{mode}][{now:%Y%m%d-%H%M%S}] {title}"
    mail_link = send_gmail_report(subject, detailed)
    print("Gmail: OK")
    telegram_text += (
        "\n\n📧 Gmail 앱 실행 테스트: googlegmail://"
        "\n※ 앱 링크가 눌리지 않거나 메일이 열리지 않으면 아래 웹 링크를 사용하세요."
        f"\n🔎 상세 메일 검색(웹): {mail_link}"
    )
    result = send_telegram_message(telegram_text)
    print("Telegram: OK")
    telegram_link = get_telegram_link(result)

    def fmt(k):
        d = market.get(k, {})
        if d.get("error") or not d:
            return "미확인"
        return f"{d['price']:,.0f}원"

    kakao_text = (f"[{title}] 삼성 {fmt('Samsung')} / SK {fmt('SK Hynix')}")
    kakao_text += ("\n텔레그램: " + telegram_link) if telegram_link else "\n텔레그램 원문 링크: 생성 불가"
    if len(kakao_text) > 180:
        raise ValueError("Kakao summary exceeds 180 characters")
    send_kakao_messages([kakao_text])
    print("Kakao: OK")
    if not telegram_link:
        print("TELEGRAM_LINK_UNAVAILABLE: private chat or no TELEGRAM_PUBLIC_USERNAME")
    return {"mode": mode, "status": "sent_stage7"}


if __name__ == "__main__":
    main()
