"""Evidence-first report; no unsupported news causality or valuation targets."""
from datetime import datetime
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")
LABELS = {"Micron":"마이크론", "NVIDIA":"엔비디아", "NASDAQ":"나스닥",
          "SOX":"필라델피아 반도체지수", "Samsung":"삼성전자", "SK Hynix":"SK하이닉스"}


def line(name, market):
    d = market.get(name, {})
    if d.get("error") or not d:
        return f"• {LABELS[name]}: 조회 불가 (가격·기준일 검증 필요)"
    unit = "원" if name in ("Samsung", "SK Hynix") else ("pt" if name in ("NASDAQ", "SOX") else "USD")
    price = f"{d['price']:,.0f}" if unit == "원" else f"{d['price']:,.2f}"
    return f"• {LABELS[name]}: {price} {unit} ({d['change']:+.2f}%) / {d['date']} 종가"


def compose(mode, market, news, news_error):
    now = datetime.now(KST)
    morning = mode == "morning"
    title = "미국장 마감 및 국내 영향 점검" if morning else "한국 정규장 마감 및 위험 요인 점검"
    us = [line(k, market) for k in ("NASDAQ", "SOX", "Micron", "NVIDIA")]
    kr = [line(k, market) for k in ("Samsung", "SK Hynix")]
    headlines = []
    for i, n in enumerate(news, 1):
        analysis = n.get("analysis")
        if analysis:
            facts = analysis.get("facts", [])
            headlines.append(
                f"{i}. {analysis['headline_ko']}\n"
                f"   한국어 요약: {analysis['summary_ko']}\n"
                + "".join(f"   핵심 사실: {fact}\n" for fact in facts[:3])
                + f"   삼성전자 영향: {analysis['samsung_impact']}\n"
                + f"   SK하이닉스 영향: {analysis['hynix_impact']}\n"
                + f"   불확실성: {analysis['uncertainty']}\n"
                + f"   검증: {n.get('verification', 'AI 요약')}\n"
                + f"   출처: {n['source']} | {n['published']}\n"
                + f"   원문: {n['link']}"
            )
        else:
            headlines.append(
                f"{i}. [원문 미검증] {n['title']}\n"
                f"   본문 미확인: 번역·요약·기업 영향 분석 보류\n"
                f"   출처: {n['source']} | {n['published']}\n"
                f"   원문: {n['link']}"
            )
    if not headlines:
        headlines = [f"최근 24시간 뉴스 확인 불가 ({news_error or '조건에 맞는 기사 없음'})."]
    def move(name):
        d=market.get(name,{})
        return d.get("change") if not d.get("error") else None
    mu,sox = move("Micron"),move("SOX")
    clues=[]
    if mu is not None and sox is not None:
        if mu < 0 and sox < 0:
            clues.append("마이크론과 반도체지수가 함께 하락했습니다. 업종 공통 요인을 점검할 필요가 있습니다.")
        elif mu * sox < 0:
            clues.append("마이크론과 반도체지수의 방향이 다릅니다. 개별 기업 요인과 업종 요인을 분리해 살펴봐야 합니다.")
        else:
            clues.append("마이크론과 반도체지수가 같은 방향입니다. 동반 움직임만으로 원인을 확정할 수는 없습니다.")
    else:
        clues.append("미국 종가 일부를 확인하지 못해 방향성 판단을 보류합니다.")
    if not morning:
        clues.append("오전 예측 기록과 국내 투자자별 매매 데이터가 연결되지 않아 전망 적중 여부·수급은 아직 검증할 수 없습니다.")
    details = (
        f"[반도체 상세 보고서] {title}\n"
        f"작성: {now:%Y-%m-%d %H:%M} KST\n\n"
        "1. 미국 시장 지표 (각 지표의 실제 거래일 표시)\n" + "\n".join(us) + "\n\n"
        "2. 한국 정규장 지표\n" + "\n".join(kr) + "\n\n"
        "3. 최근 24시간 관련 뉴스 (자동 수집 제목, 기사 본문 미검증)\n" + "\n\n".join(headlines) + "\n\n"
        "4. 시장 해석: 관찰과 가설 구분\n" + "\n".join("• "+x for x in clues) + "\n"
        "• 뉴스가 가격 변동의 원인인지 확인되지 않았으므로 인과관계로 단정하지 않습니다.\n\n"
        "5. 삼성전자·SK하이닉스 관찰 조건\n"
        "• 미국 메모리주 및 SOX와 국내 주가의 동행·괴리를 비교합니다.\n"
        "• HBM 수주, 메모리 가격, 실적 가이던스의 실제 발표 여부를 원문으로 검증해야 합니다.\n"
        "• 투자 판단은 보유 비중·현금 수요·변동성 등을 함께 고려해야 하며 이 보고서는 매매 지시가 아닙니다.\n\n"
        "6. 데이터 및 해석 한계\n"
        "• 가격: Yahoo Finance 일별 데이터. 지연·휴장 시 마지막 거래일 가격일 수 있습니다.\n"
        "• 뉴스: Google News RSS 검색 결과. 기사 제목만으로 긍정·부정 판단을 확정하지 않습니다.\n"
        "• PER 비교: 기존 forward/trailing 기간 불일치 가능성 때문에 검증 전까지 목표주가를 제외합니다.\n"
        "• 국내 외국인·기관 수급, 오전 예측의 저장/사후 검증, NXT 가격은 아직 미구현입니다."
    )
    telegram = (
        f"[{title}]\n{now:%m/%d %H:%M} KST\n"
        + "\n".join(us + kr)
        + "\n\n[핵심 관찰]\n" + "\n".join("• "+x for x in clues)
        + "\n\n[주요 뉴스]\n"
        + "\n".join("• "+x["title"][:100] for x in news[:3])
        + ("\n• 확인된 기사 없음" if not news else "")
    )
    return title,details,telegram
