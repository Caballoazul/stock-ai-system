"""Standalone Gemini connection check. Does not send reports or access news."""
import os
import sys
import requests

BASE = "https://generativelanguage.googleapis.com/v1beta"
key = os.getenv("GEMINI_API_KEY", "").strip()
if not key:
    print("GEMINI_CHECK=FAIL reason=missing_key")
    sys.exit(1)
headers = {"x-goog-api-key": key, "Content-Type": "application/json"}
try:
    listing = requests.get(BASE + "/models", headers=headers, timeout=20)
    print("GEMINI_MODELS_HTTP=" + str(listing.status_code))
    if listing.status_code != 200:
        sys.exit(1)
    models = listing.json().get("models", [])
    supported = [m["name"] for m in models if "generateContent" in m.get("supportedGenerationMethods", [])]
    print("GEMINI_GENERATE_MODELS=" + str(len(supported)))
    preferred = ["models/gemini-3.5-flash-lite", "models/gemini-3.5-flash", "models/gemini-2.5-flash"]
    selected = next((name for name in preferred if name in supported), None)
    if selected is None:
        print("GEMINI_CHECK=FAIL reason=preferred_models_unavailable")
        sys.exit(1)
    if not selected:
        print("GEMINI_CHECK=FAIL reason=no_supported_model")
        sys.exit(1)
    print("GEMINI_TEST_MODEL=" + selected)
    payload = {"contents": [{"parts": [{"text": "다음 한 단어를 한국어로 번역하세요: semiconductor"}]}]}
    result = requests.post(BASE + "/" + selected + ":generateContent",
                           headers=headers, json=payload, timeout=35)
    print("GEMINI_GENERATE_HTTP=" + str(result.status_code))
    if result.status_code != 200:
        try:
            err = result.json().get("error", {})
            print("GEMINI_ERROR_STATUS=" + str(err.get("status", "unknown"))[:60])
            print("GEMINI_ERROR_MESSAGE=" + str(err.get("message", "unknown"))[:250].replace("\n", " "))
        except ValueError:
            print("GEMINI_ERROR_STATUS=non_json_response")
        print("GEMINI_CHECK=FAIL")
        sys.exit(1)
    parts = result.json().get("candidates", [{}])[0].get("content", {}).get("parts", [])
    output = "".join(part.get("text", "") for part in parts).strip()
    if not output:
        print("GEMINI_CHECK=FAIL reason=empty_response")
        sys.exit(1)
    print("GEMINI_RESPONSE=" + output[:100].replace("\n", " "))
    print("GEMINI_CHECK=PASS")
except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as exc:
    print("GEMINI_CHECK=FAIL reason=" + type(exc).__name__)
    sys.exit(1)
