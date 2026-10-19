"""Attach a historical financial-validation fixture to a market report safely.

Does not fetch new data, alter the source report, or assert current-period verification.
"""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path

REQUIRED_MARKET_KEYS = {'schema_version', 'generated_at_kst', 'market'}
REQUIRED_FINANCIAL_KEYS = {'schema_version', 'company', 'source_review', 'earnings_quality_review', 'limitations'}


def merge_financial_validation(market: dict, fixture: dict) -> dict:
    if not isinstance(market, dict) or not REQUIRED_MARKET_KEYS.issubset(market):
        raise ValueError('InvalidMarketPayload')
    if not isinstance(market['market'], dict):
        raise ValueError('InvalidMarketSection')
    if not isinstance(fixture, dict) or not isinstance(fixture.get('financial_validation'), dict):
        raise ValueError('InvalidFinancialFixture')
    fv = fixture['financial_validation']
    if not REQUIRED_FINANCIAL_KEYS.issubset(fv):
        raise ValueError('MissingFinancialFields')
    company = fv['company']
    source = fv['source_review']
    if not isinstance(company, dict) or not isinstance(source, dict):
        raise ValueError('InvalidFinancialMetadata')
    if company.get('corp_code') != '00164779' or str(company.get('year')) != '2026' or company.get('report_code') != '11012' or company.get('fs_div') != 'CFS':
        raise ValueError('UnexpectedFixturePeriodOrCompany')
    if source.get('status') != 'matched' or source.get('matched_count') != 6 or source.get('expected_count') != 6 or source.get('mismatches') or source.get('errors'):
        raise ValueError('UnmatchedFinancialFixture')
    if 'financial_validation' in market:
        raise ValueError('AlreadyHasFinancialValidation')
    result = copy.deepcopy(market)
    result['financial_validation'] = copy.deepcopy(fv)
    result['financial_validation']['data_role'] = 'historical_reference'
    result['financial_validation']['current_period_verified'] = False
    result['financial_validation']['source_review']['source_verified_scope'] = 'supplied_manual_evidence_record_only'
    return result


def build_preview(market_path: Path, fixture_path: Path, output_path: Path) -> dict:
    market_path = market_path.resolve()
    fixture_path = fixture_path.resolve()
    output_path = output_path.resolve()
    if output_path == market_path or output_path == fixture_path or output_path.name == 'market_analysis.json':
        raise ValueError('ProductionOrSourceOverwriteForbidden')
    market = json.loads(market_path.read_text(encoding='utf-8'))
    fixture = json.loads(fixture_path.read_text(encoding='utf-8'))
    result = merge_financial_validation(market, fixture)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--market', default='reports/market_analysis.json')
    parser.add_argument('--fixture', default='tests/fixtures/financial_validation_test_v1.json')
    parser.add_argument('--output', default='reports/market_analysis_financial_preview.json')
    args = parser.parse_args()
    result = build_preview(Path(args.market), Path(args.fixture), Path(args.output))
    print('INTEGRATION_PREVIEW_OK', args.output, result['financial_validation']['data_role'])
