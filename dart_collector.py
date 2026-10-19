"""Open DART reported financial statement collector (not analyst forecasts)."""
from datetime import datetime
from zoneinfo import ZoneInfo
import requests

BASE_URL = 'https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json'
CORP_CODES = {'Samsung': '00126380', 'SK Hynix': '00164779'}
REPORT_CODES = {'annual': '11011', 'q1': '11013', 'half': '11012', 'q3': '11014'}

def normalize(payload, corp_code, year, report_code, fs_div, collected_at=None):
    result = {
        'corp_code': corp_code, 'year': str(year), 'report_code': report_code,
        'fs_div': fs_div, 'source': 'Open DART / fnlttSinglAcntAll',
        'collected_at_kst': collected_at or datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds'),
        'status': 'unavailable', 'error': None, 'accounts': [],
        'period_verified': False,
    }
    if not isinstance(payload, dict):
        result.update(status='error', error='InvalidResponse')
        return result
    if payload.get('status') != '000':
        result['status'] = 'unavailable' if payload.get('status') == '013' else 'error'
        result['error'] = 'DARTStatus:' + str(payload.get('status', 'unknown'))
        return result
    rows = payload.get('list')
    if not isinstance(rows, list):
        result.update(status='error', error='MissingAccountList')
        return result
    # Preserve raw account values and their original period labels. Do not
    # mistake cumulative quarter values for stand-alone quarter earnings.
    for row in rows:
        if not isinstance(row, dict):
            continue
        result['accounts'].append({k: row.get(k) for k in (
            'account_id', 'account_nm', 'sj_div', 'fs_div',
            'thstrm_nm', 'thstrm_amount', 'thstrm_add_amount',
            'frmtrm_nm', 'frmtrm_amount', 'frmtrm_add_amount',
            'bfefrmtrm_nm', 'bfefrmtrm_amount', 'currency', 'ord',
        )})
    result['status'] = 'ok' if result['accounts'] else 'unavailable'
    return result

def collect_statement(corp_code, year, report_code, api_key, *, fs_div='CFS', session=None):
    """Use explicit fiscal year/report; do not guess latest available filing."""
    if corp_code not in CORP_CODES.values():
        raise ValueError('Unknown corp code')
    if report_code not in REPORT_CODES.values() or fs_div not in ('CFS', 'OFS'):
        raise ValueError('Invalid report code or statement scope')
    if not (isinstance(year, int) and 2000 <= year <= 2100 and api_key):
        raise ValueError('Year and API key required')
    session = session or requests.Session()
    try:
        response = session.get(BASE_URL, params={
            'crtfc_key': api_key, 'corp_code': corp_code,
            'bsns_year': str(year), 'reprt_code': report_code, 'fs_div': fs_div,
        }, timeout=15)
        response.raise_for_status()
        return normalize(response.json(), corp_code, year, report_code, fs_div)
    except (requests.RequestException, ValueError, TypeError) as exc:
        result = normalize(None, corp_code, year, report_code, fs_div)
        result['error'] = type(exc).__name__
        return result
