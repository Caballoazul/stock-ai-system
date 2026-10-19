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


def complete_sentence(value, max_chars=180):
    """Keep whole sentences; never cut a word or sentence midstream."""
    import re
    text = " ".join(str(value or "").split())
    if len(text) <= max_chars:
        return text
    sentences = re.split(r"(?<=[.!?。])\\s+", text)
    selected = []
    for sentence in sentences:
        candidate = " ".join(selected + [sentence])
        if len(candidate) > max_chars:
            break
        selected.append(sentence)
    if selected:
        return " ".join(selected)
    return text  # Prefer complete meaning over arbitrary truncation.


def news_section(item):
    """Heuristic category, not a verified causal explanation."""
    title = str(item.get("title", "")).lower()
    market_terms = ("shares", "stocks", "selloff", "slump", "decline", "fall",
                    "drop", "rally", "funding", "earnings", "guidance",
                    "downgrade", "upgrade", "tariff", "market", "investors",
                    "주가", "하락", "급락", "실적")
    industry_terms = ("hbm", "nvhbm", "base die", "process", "node",
                      "manufacturing", "packaging", "foundry", "supply chain",
                      "공정", "양산", "공급망")
    if any(term in title for term in market_terms):
        return "시장 변동 관련"
    if any(term in title for term in industry_terms):
        return "산업·기술 동향"
    return "기타 반도체 뉴스"


def compose(mode, market, news, news_error):
    now = datetime.now(KST)
    morning = mode == "morning"
    title = "미국장 마감 및 국내 영향 점검" if morning else "한국 정규장 마감 및 위험 요인 점검"
    us = [line(k, market) for k in ("NASDAQ", "SOX", "Micron", "NVIDIA")]
    kr = [line(k, market) for k in ("Samsung", "SK Hynix")]
    headlines = []
    for i, n in enumerate(news, 1):
        section = news_section(n)
        analysis = n.get("analysis")
        if analysis:
            facts = analysis.get("facts", [])
            headlines.append(
                f"{i}. [{section}] {analysis['headline_ko']}\n"
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
                f"{i}. [{section} · 원문 미검증] {n['title']}\n"
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
    # Evidence tiers: a verified article body is not proof of market causality.
    evidence = []
    verified = [n for n in news if n.get("analysis") and "본문 확보" in n.get("verification", "")]
    if verified:
        for n in verified[:2]:
            analysis = n["analysis"]
            facts = analysis.get("facts") or []
            if facts:
                evidence.append("• [기사 근거·원문 대조 필요] " + str(facts[0])[:220]
                                + " (출처: " + str(n.get("source", "미확인")) + ")")
            else:
                evidence.append("• [기사 본문 확보] " + str(analysis.get("headline_ko", n["title"]))[:180])
    else:
        evidence.append("• [기사 근거 부족] 분석 가능한 기사 본문을 확보하지 못했습니다.")
    evidence.append("• [시장 관찰] " + clues[0])
    evidence.append("• [가설·미검증] 관련 뉴스가 당일 주가 변동을 일으켰는지는 확인되지 않았습니다.")
    evidence.append("• [추가 확인] 발표 시각과 가격 반응, 기업 공시·실적·가이던스 등 독립 근거를 대조해야 합니다.")
    if not morning:
        clues.append("오전 예측 기록과 국내 투자자별 매매 데이터가 연결되지 않아 전망 적중 여부·수급은 아직 검증할 수 없습니다.")
    details = (
        f"[반도체 상세 보고서] {title}\n"
        f"작성: {now:%Y-%m-%d %H:%M} KST\n\n"
        "1. 미국 시장 지표 (각 지표의 실제 거래일 표시)\n" + "\n".join(us) + "\n\n"
        "2. 한국 정규장 지표\n" + "\n".join(kr) + "\n\n"
        "3. 최근 24시간 관련 뉴스 (본문 확보 여부 및 번역 검증 상태 구분)\n" + "\n\n".join(headlines) + "\n\n"
        "4. 시장 해석: 확인 근거·관찰·가설 구분\n" + "\n".join(evidence) + "\n"
        "• 뉴스가 가격 변동의 원인인지 확인되지 않았으므로 인과관계로 단정하지 않습니다.\n\n"
        "5. 삼성전자·SK하이닉스 관찰 조건\n"
        "• 미국 메모리주 및 SOX와 국내 주가의 동행·괴리를 비교합니다.\n"
        "• HBM 수주, 메모리 가격, 실적 가이던스의 실제 발표 여부를 원문으로 검증해야 합니다.\n"
        "• 투자 판단은 보유 비중·현금 수요·변동성 등을 함께 고려해야 하며 이 보고서는 매매 지시가 아닙니다.\n\n"
        "6. 데이터 및 해석 한계\n"
        "• 가격: Yahoo Finance 일별 데이터. 지연·휴장 시 마지막 거래일 가격일 수 있습니다.\n"
        "• 뉴스: 언론사 RSS 우선, GDELT·Google News 예비 경로. 기사 본문 확보와 독립 검증은 다릅니다.\n"
        "• PER 비교: 기존 forward/trailing 기간 불일치 가능성 때문에 검증 전까지 목표주가를 제외합니다.\n"
        "• 국내 외국인·기관 수급, 오전 예측의 저장/사후 검증, NXT 가격은 아직 미구현입니다."
    )
    # Telegram-only layout: separate price observations from unverified causes.
    us_dates = [market.get(k, {}).get("date") for k in ("SOX", "NASDAQ", "Micron")]
    us_session = max((d for d in us_dates if isinstance(d, str) and d), default=None)
    def session_match(item):
        return bool(us_session and item.get("session_date") == us_session)
    verified_news = sorted(
        [n for n in news if n.get("analysis") and "본문 확보" in n.get("verification", "")],
        key=lambda n: (not session_match(n), news_section(n) != "시장 변동 관련"))
    # Only session-matched articles can be described as evidence candidates
    # for that US session; other verified articles remain industry context.
    def topic_key(item):
        title = str(item.get("title", "")).lower().replace("nvhbm", "hbm")
        if "hbm" in title and ("tsmc" in title or "3nm" in title or "3나노" in title):
            return "tsmc-hbm-base-die"
        return " ".join(sorted(set(__import__("re").findall(r"[a-z0-9가-힣]{4,}", title))))[:120]

    used_topics = {topic_key(n) for n in verified_news[:2]}
    references = []
    for item in news:
        if item in verified_news[:2] or topic_key(item) in used_topics:
            continue
        references.append(item)
        used_topics.add(topic_key(item))
        if len(references) == 2:
            break

    market_related = [n for n in verified_news if session_match(n) and news_section(n) == "시장 변동 관련"]
    cause = ("• 시장 변동 관련 기사 본문은 확보했으나, 미국장 하락과의 인과관계는 미검증입니다."
             if market_related else
             "• 미국장 하락 원인 미확인: 확보한 기사로는 당일 하락 이유를 입증할 수 없습니다.")
    compare = "• 미국과 한국 시장의 거래일이 다르므로 종가·등락률을 구분해 비교해야 합니다."
    if mu is not None and sox is not None:
        compare += "\\n• " + clues[0]

    telegram_news = []
    for item in verified_news[:2]:
        analysis = item["analysis"]
        heading = analysis.get("headline_ko") or item.get("title", "제목 없음")
        label = ("미국장 거래일 관련" if session_match(item) else
                 "산업·기술 및 후속 동향" if news_section(item) == "시장 변동 관련" else news_section(item))
        telegram_news.append("• [" + label + "] " + str(heading))
        telegram_news.append("  요약: " + complete_sentence(analysis.get("summary_ko", "요약 없음"), 180))
        telegram_news.append("  삼성: " + complete_sentence(analysis.get("samsung_impact", "확인 불가"), 130))
        telegram_news.append("  하이닉스: " + complete_sentence(analysis.get("hynix_impact", "확인 불가"), 130))
        telegram_news.append("  근거: 기사 본문 확보·AI 분석, 독립 검증 전")
        telegram_news.append("  출처: " + str(item.get("source", "미확인"))
                             + " / " + str(item.get("published", "시각 미확인")))
        if item.get("link"):
            telegram_news.append("  원문: " + str(item["link"]))
    if not verified_news:
        telegram_news.append("• 기사 본문 확보 실패 · 뉴스 해석 보류")
    telegram_news.append("• 기사 속 주가·등락률은 보도 시점 수치일 수 있으며, 위 종가와 다를 수 있습니다.")
    if references:
        telegram_news.append("[참고 뉴스 · 본문 미확인]" if all(item not in verified_news for item in references) else "[추가 참고 뉴스 · 검증 상태 개별 표시]")
        for item in references:
            telegram_news.append("• [" + news_section(item) + "] " + str(item.get("title", "제목 없음")))
            telegram_news.append("  " + ("본문 확보·AI 분석, 독립 검증 전" if item in verified_news else "제목만 참고 · 사실관계 및 기업 영향 미검증"))
            if item.get("link") and not item["link"].startswith("https://news.google.com/"):
                telegram_news.append("  링크: " + str(item["link"]))
    telegram = (
        f"[{title}]\n{now:%m/%d %H:%M} KST\n"
        + "\n".join(us[:4])
        + "\n\n[미국장 변동 원인]\n" + cause
        + "\n\n[국내 종목]\n" + "\n".join(kr)
        + "\n\n[국내 영향·비교]\n" + compare
        + "\n\n[핵심 뉴스·근거]\n" + "\n".join(telegram_news)
        + "\n\n[판단 유보] 뉴스와 당일 등락의 인과관계 미검증."
        + "\n[추가 확인] 발표 시각·기업 공시·실적을 대조해야 합니다."
    )
    return title,details,telegram
