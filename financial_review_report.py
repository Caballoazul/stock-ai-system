"""Render a historical financial review for a Gmail detailed report.

This module does not fetch data or send messages.
"""
import json
from pathlib import Path


def format_financial_review(payload: dict) -> str:
    if not isinstance(payload, dict):
        raise ValueError('InvalidPayload')
    fv = payload.get('financial_validation')
    if not isinstance(fv, dict):
        raise ValueError('MissingFinancialValidation')
    company = fv.get('company')
    source = fv.get('source_review')
    quality = fv.get('earnings_quality_review')
    if not all(isinstance(x, dict) for x in (company, source, quality)):
        raise ValueError('InvalidReviewSections')
    if (fv.get('data_role') != 'historical_reference'
            or fv.get('current_period_verified') is not False
            or company.get('corp_code') != '00164779'
            or str(company.get('year')) != '2026'
            or company.get('report_code') != '11012'
            or company.get('fs_div') != 'CFS'):
        raise ValueError('UnexpectedCompanyPeriodOrRole')
    if (source.get('status') != 'matched'
            or source.get('matched_count') != 6
            or source.get('expected_count') != 6
            or source.get('mismatches')
            or source.get('errors')
            or source.get('source_verified_scope') != 'supplied_manual_evidence_record_only'):
        raise ValueError('ReviewNotValidated')
    flags = quality.get('flags')
    if not isinstance(flags, list) or not all(isinstance(x, str) for x in flags):
        raise ValueError('InvalidQualityFlags')
    explanations = {
        'MaterialFinancialInstrumentValuationGain': '금융상품 평가이익의 영향이 중요하여 추가 확인이 필요합니다.',
        'NetIncomeExceedsOperatingIncome': '순이익이 영업이익보다 커 영업외손익 구성을 확인해야 합니다.',
    }
    lines = [
        '[재무검증 참고자료 — 과거 공시]',
        '기업: SK하이닉스 / 2026년 반기보고서 / 연결재무제표(CFS)',
        '자료 성격: 과거 실적 참고자료 (현재 분기 검증 완료 아님)',
        '대조 결과: 제공된 수기 공시 근거와 DART API 금액 6개 항목 일치',
        '검증 범위: 입력된 수기 대조 기록과 API 결과의 일치 여부만 확인',
        '공시 원본의 진위 및 검토자 신원은 자동으로 독립 검증되지 않았습니다.',
        '이익의 질: ' + ('추가 검토 필요' if flags else '등록된 주의 신호 없음 (양호 판정 아님)'),
    ]
    for flag in flags:
        lines.append('• ' + explanations.get(flag, f'추가 확인 항목: {flag}'))
    ratio = quality.get('metrics', {}).get('valuation_gain_to_operating_income') if isinstance(quality.get('metrics'), dict) else None
    if isinstance(ratio, (int, float)) and not isinstance(ratio, bool):
        lines.append(f'• 금융상품 평가이익/영업이익: {ratio * 100:.2f}% (과거 반기 기준)')
    lines.append('본 항목은 매수·매도 의견 또는 최신 실적 검증 결과가 아닙니다.')
    return '\n'.join(lines)


def render_from_file(path: str | Path) -> str:
    payload = json.loads(Path(path).read_text(encoding='utf-8'))
    return format_financial_review(payload)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='reports/market_analysis_financial_preview.json')
    args = parser.parse_args()
    print(render_from_file(args.input))
