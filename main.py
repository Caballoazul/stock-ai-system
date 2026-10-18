"""Semiconductor reports: AM/PM Gmail, Telegram, Kakao; NXT pending."""
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from micron_per import get_micron_data
from samsung_per import get_samsung_data
from skhynix_per import get_skhynix_data
from analysis import build_quant_dataframe, make_analysis
from report import build_market_report, build_valuation_report, build_quant_report, build_ai_report
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

    df = make_analysis(build_quant_dataframe([
        get_micron_data(), get_samsung_data(), get_skhynix_data()
    ]))
    title = "08:00 미국장 분석" if mode == "morning" else "16:30 한국 정규장 분석"
    subject = f"[반도체보고서][{mode}][{now:%Y%m%d-%H%M%S}] {title}"
    sections = [build_market_report(df), build_valuation_report(df),
                build_quant_report(df), build_ai_report(df)]
    note = ("※ PER 비교는 가정에 따른 상대가치 시나리오이며 매매 권고가 아닙니다.\n"
            "※ 가격의 실제 기준시각·수급·뉴스·오전 전망 대비 실적 검증은 아직 미구현입니다.")
    detailed = f"{title}\n작성시각: {now:%Y-%m-%d %H:%M} KST\n\n" + "\n\n".join(sections) + "\n\n" + note
    # Fail closed if Gmail fails, so Telegram never links to an unsent report.
    mail_link = send_gmail_report(subject, detailed)
    print("Gmail: OK")
    telegram_text = (
        f"[{title}]\n{now:%Y-%m-%d %H:%M} KST\n\n"
        f"MU {short_price(df, 'Micron')}\n"
        f"삼성전자 {short_price(df, 'Samsung', True)}\n"
        f"SK하이닉스 {short_price(df, 'SK Hynix', True)}\n\n"
        "PER 상대가치 분석은 참고용 시나리오입니다.\n"
        "수급·뉴스·전망 검증은 아직 제공되지 않습니다.\n\n"
        f"지메일 상세 보고서 검색: {mail_link}"
    )
    result = send_telegram_message(telegram_text)
    print("Telegram: OK")
    telegram_link = get_telegram_link(result)
    kakao_text = make_kakao_summary(df, mode, telegram_link)
    send_kakao_messages([kakao_text])
    print("Kakao: OK")
    if not telegram_link:
        print("TELEGRAM_LINK_UNAVAILABLE: private chat or no TELEGRAM_PUBLIC_USERNAME")
    return {"mode": mode, "status": "sent_stage4"}


if __name__ == "__main__":
    main()
