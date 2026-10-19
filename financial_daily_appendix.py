"""Opt-in, historical-only Gmail appendix; no I/O other than reading a local fixture.

The fixture is a manually reviewed historical test record, not live DART data.
"""
from __future__ import annotations
import json
from pathlib import Path
from financial_validation_integration import merge_financial_validation
from financial_review_report import format_financial_review

DEFAULT_FIXTURE = Path('tests/fixtures/financial_validation_test_v1.json')


def append_daily_financial_review(detailed: str, enabled: bool = False,
                                  fixture_path: str | Path = DEFAULT_FIXTURE) -> str:
    if not isinstance(detailed, str):
        raise TypeError('DetailedReportMustBeString')
    if not enabled:
        return detailed
    try:
        fixture = json.loads(Path(fixture_path).read_text(encoding='utf-8'))
        # This metadata is required by the existing safe merge function. It is
        # NOT a current market snapshot and is never used for price analysis.
        historical_context = {
            'schema_version': 1,
            'generated_at_kst': 'historical-fixture-only',
            'market': {},
        }
        validated = merge_financial_validation(historical_context, fixture)
        appendix = format_financial_review(validated)
    except (OSError, ValueError, TypeError, KeyError, UnicodeError) as exc:
        print(f'FINANCIAL_APPENDIX_SKIPPED={type(exc).__name__}')
        return detailed
    return detailed + '\n\n' + appendix
