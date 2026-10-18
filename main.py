"""Semiconductor reports: AM/PM Gmail, Telegram, Kakao; NXT pending."""
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from micron_per import get_micron_data
from samsung_per import get_samsung_data
from skhynix_per import get_skhynix_data
from analysis import build_quant_dataframe, make_analysis
from market_intelligence import fetch_market, fetch_news
from insight_report import compose
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


def row_value(df, company, key):
    found = df[df["Company"] == company]
    if found.empty:
        return None
    try:
        value = float(found.iloc[0][key])
        return value if value == value and value > 0 else None
    except (ValueError, TypeError, KeyError):
        return None


def short_price(df, company, won=False):
    value = row_value(df, company, "Price")
    if value is None:
        return "미확인"
    return f"{value:,.0f}원" if won else f"${value:,.2f}"


def make_kakao_summary(df, mode, telegram_link=None):
    title = "미국장" if mode == "morning" else "한국 정규장"
    msg = (f"[{title} {datetime.now(KST):%m/%d}] "
           f"MU {short_price(df, 'Micron')} / "
           f"삼성 {short_price(df, 'Samsung', True)} / "
           f"SK {short_price(df, 'SK Hynix', True)}")
    if telegram_link:
        msg += "\n텔레그램: " + telegram_link
    else:
        msg += "\n텔레그램 원문 링크: 생성 불가"
    if len(msg) > 180:
        raise ValueError("Kakao summary exceeds 180 characters")
    return msg


def get_telegram_link(response):
    """Private chat IDs have no universally accessible per-message URL.
    Only public username/channel links can be built reliably here."""
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
    return {"mode": mode, "status": "sent_stage5"}


if __name__ == "__main__":
    main()
