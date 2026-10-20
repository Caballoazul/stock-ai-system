# 2026-10-20 반도체 실데이터 예약 연계 브리핑

- 작성·검증 기준: 2026-10-20 12:56 KST
- 기사 조회 범위: 2026-10-19 12:56 ~ 2026-10-20 12:56 KST
- 검증 방법: 기사 본문 직접 열람 또는 원문을 전재한 Reuters 기사 본문 열람
- 성격: GitHub 저장·재조회·Gmail 발송 검증용. 매수·매도 권유 아님.
- 주의: 2026-10-20 한국 증시는 아직 정규장 진행 중. 당일 종가·확정 투자자별 수급을 기재하지 않음.

## 1. 미국 AI·반도체주, 전주 급락 이후 반등
- 제목: AI stocks bounce back after bruising selloff, CoreWeave gets Goldman upgrade
- 출처: Reuters / Investing.com에 게재된 Reuters 기사
- 최초 게시: 2026-10-19 08:41 미국 동부시간(2026-10-19 21:41 KST), 업데이트 11:18 ET
- 링크: https://www.investing.com/news/stock-market-news/us-chip-stocks-rise-after-steepest-weekly-selloff-in-months-4957420
- **확인 사실:** 미국 AI 관련 주식이 전주 급락 후 반등했다. 로이터가 보도한 거래 중 시점에 엔비디아, AMD, 마이크론 등이 상승했다. 마이크론은 당시 약 4.2% 올랐지만 이는 기사의 장중 수치로 종가가 아니다. AI 인프라 기업 CoreWeave의 차입 비용과 AI 투자 수익성에 대한 우려는 여전히 남았다.
- **시사점(해석):** 반도체주 단기 반등은 투자심리 회복 신호일 수 있지만, 메모리 실수요와 국내 두 기업의 향후 주가를 직접 입증하지는 않는다.

## 2. 엔비디아 Vera CPU, AI 클라우드 업체 Modal 신규 채택
- 제목: Nvidia wins fast-growing AI startup Modal for new central processors
- 출처: Reuters / Euronext 게재 Reuters 기사
- 보도: 2026-10-19 10:11 미국 동부시간(2026-10-19 23:11 KST); Euronext 게재 시각은 현지 기준 16:12로 표시
- 링크: https://live.euronext.com/en/financial-news/nvidia-wins-fast-growing-ai-startup-modal-new-central-processors
- **확인 사실:** AI 클라우드 업체 Modal은 엔비디아의 Vera CPU를 AI 에이전트용 컴퓨팅에 도입하기로 했다. 초기 시험에서 처리량 개선을 보고했지만 Intel·AMD 제품을 전면 교체하지 않고 혼용할 계획이라고 밝혔다.
- **시사점(해석):** AI 인프라의 CPU 공급업체 다변화와 연산 수요를 보여 주지만, 삼성전자·SK하이닉스의 HBM 공급 계약 체결이나 매출 증가를 뜻하는 직접 증거는 아니다.

## 3. 미국 AI주 반등 속 한국 코스피도 10월 19일 회복
- 제목: AI stocks lead a rebound on Wall Street as European markets drop following protests
- 출처: Associated Press (AP)
- 보도: 2026-10-19 미국 현지 날짜 확인. 원문 화면에서 분 단위 게시 시각은 확인되지 않음.
- 링크: https://apnews.com/article/stocks-markets-oil-us-ai-494fbe4361a0360b2f6368e7a6d8f058
- **확인 사실:** 10월 19일 미국 나스닥은 1.1%, S&P500은 0.4% 상승했다. AP는 같은 날 한국 코스피가 약 1.8% 반등했으며 삼성전자·SK하이닉스가 한국 지수에 큰 영향을 준다고 설명했다. 이는 10월 19일의 시장 요약이지 10월 20일 한국장 종가가 아니다.
- **시사점(해석):** AI 업종 회복이 지수에 영향을 미치지만, 업종 반등이 국내 개별 종목의 지속 상승으로 이어지는지는 별도 확인해야 한다.

## 삼성전자·SK하이닉스 관찰 사항
- **삼성전자:** 이번 조회에서 최근 24시간 내 공식 신규 HBM 계약·실적 공시를 별도 확인하지 못함. 10월 20일 장중 및 종가 숫자는 검증하지 않아 기재하지 않음.
- **SK하이닉스:** 이번 조회에서 최근 24시간 내 공식 신규 HBM 계약·실적 공시를 별도 확인하지 못함. 10월 20일 확정 외국인·기관 순매매는 장 마감 전이므로 기재하지 않음.
- **핵심 점검:** 미국 마이크론 반등과 국내 메모리주의 동조 여부는 한국장 종료 후 가격 및 확정 수급과 대조해야 함.

## GitHub PER 결합 검증
- 확인 코드: valuation_collector.py (Yahoo Finance / yfinance에서 MU, 005930.KS, 000660.KS의 trailingPE, forwardPE 등을 수집하도록 구현)
- 확인 코드: per_comparison.py (3사 Trailing PER·Forward PER 비교 형식 구현)
- 확인 데이터: reports/market_analysis.json
- 기존 보고서 생성 시각: 2026-10-18T23:38:10+09:00
- 기존 보고서 시세 기준일: 2026-10-16
- **검증 결과:** 위 JSON에는 주가·변동률·거래량만 있고, 3사의 trailing_pe·forward_pe 또는 실제 수집 시각이 기록된 PER 값은 없음. reports/ 디렉터리에서 별도 PER 결과 파일을 확인하지 못함.
- **PER 데이터 미확보 — GitHub 계산 단계 미검증**
- Trailing PER / Forward PER: 마이크론·삼성전자·SK하이닉스 모두 미확인 (임의 수치 기재하지 않음).
- 주의: 소스 코드 존재는 PER 계산의 실제 실행이나 최신 수치 검증을 뜻하지 않음. 각 기업의 EPS 기준 기간 및 Forward 추정기간은 별도 검증 필요.

## 핵심 요약
1. 10월 19일 미국 AI·반도체주는 급락 후 반등했으나 차입 비용 및 투자 수익성 우려는 잔존한다.
2. 엔비디아 Vera CPU의 고객 확대는 확인됐으나 국내 메모리 2사의 신규 HBM 수주를 직접 입증하지 않는다.
3. 기존 GitHub 보고서에는 검증 가능한 PER 값이 없어 이번 테스트는 뉴스 저장 및 Gmail 전송 경로만 검증하며 PER 자동 계산은 검증하지 못한다.

---
- 저장 범위: tests/semiconductor_scheduled_real_20261020.md 신규 생성만 허용
- 기존 운영 코드, Actions, Secrets, 정규 예약, Telegram, KakaoTalk: 변경·실행 금지
