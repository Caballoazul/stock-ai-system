"""KakaoTalk self-chat sender for the existing semiconductor report.

Uses a short-lived access token derived from the refresh token in GitHub Secrets.
If Kakao rotates the refresh token, persists it before sending messages.
"""
import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

TOKEN_URL = 'https://kauth.kakao.com/oauth/token'
SEND_URL = 'https://kapi.kakao.com/v2/api/talk/memo/default/send'
MAX_TEXT_LENGTH = 180  # conservative limit for Kakao default text template


class KakaoDeliveryError(RuntimeError):
    pass


def _post(url, data, headers=None):
    request = urllib.request.Request(url, data=data, headers=headers or {}, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise KakaoDeliveryError(f'KAKAO_HTTP_{exc.code}') from None
    except (urllib.error.URLError, TimeoutError):
        raise KakaoDeliveryError('KAKAO_NETWORK_ERROR') from None


def _refresh_access_token():
    rest_key = os.getenv('KAKAO_REST_API_KEY')
    refresh_token = os.getenv('KAKAO_REFRESH_TOKEN')
    if not rest_key or not refresh_token:
        raise KakaoDeliveryError('KAKAO_CONFIG_MISSING')

    data = urllib.parse.urlencode({
        'grant_type': 'refresh_token',
        'client_id': rest_key,
        'refresh_token': refresh_token,
    }).encode('utf-8')
    result = _post(TOKEN_URL, data)
    access_token = result.get('access_token')
    if not access_token:
        raise KakaoDeliveryError('KAKAO_ACCESS_TOKEN_MISSING')

    rotated_token = result.get('refresh_token')
    if rotated_token:
        repo = os.getenv('GH_REPO')
        gh_token = os.getenv('GH_TOKEN')
        if not repo or not gh_token:
            raise KakaoDeliveryError('GITHUB_SECRET_UPDATE_CONFIG_MISSING')
        try:
            process = subprocess.run(
                ['gh', 'secret', 'set', 'KAKAO_REFRESH_TOKEN', '--repo', repo],
                input=rotated_token, text=True, capture_output=True, timeout=30,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            raise KakaoDeliveryError('GITHUB_SECRET_UPDATE_FAILED') from None
        if process.returncode != 0:
            raise KakaoDeliveryError('GITHUB_SECRET_UPDATE_FAILED')
        print('Kakao rotated refresh token saved to GitHub Secrets')
    return access_token


def _split_text(text, limit=MAX_TEXT_LENGTH):
    """Keep all characters in order, preferring newline boundaries."""
    if not isinstance(text, str) or not text.strip():
        raise KakaoDeliveryError('KAKAO_EMPTY_MESSAGE')
    chunks = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        cut = text.rfind('\n', 1, limit + 1)
        if cut <= 0:
            cut = limit
            chunks.append(text[:cut])
            text = text[cut:]
        else:
            chunks.append(text[:cut + 1])
            text = text[cut + 1:]
    return chunks


def _send_chunk(access_token, chunk):
    template = {
        'object_type': 'text',
        'text': chunk,
        'link': {'web_url': 'https://www.kakao.com/', 'mobile_web_url': 'https://www.kakao.com/'},
    }
    body = urllib.parse.urlencode({
        'template_object': json.dumps(template, ensure_ascii=False),
    }).encode('utf-8')
    result = _post(SEND_URL, body, {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/x-www-form-urlencoded',
    })
    if result.get('result_code') != 0:
        raise KakaoDeliveryError('KAKAO_SEND_REJECTED')


def send_kakao_messages(messages):
    """Send the same four report sections, splitting each for Kakao text limits."""
    access_token = _refresh_access_token()
    sent = 0
    for message in messages:
        for chunk in _split_text(message):
            _send_chunk(access_token, chunk)
            sent += 1
            time.sleep(0.4)
    print(f'Kakao Send : OK ({sent} message chunks)')
    return sent
