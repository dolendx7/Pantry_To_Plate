import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pantrytoplate.settings')
django.setup()

import requests
import json

api_key = os.getenv('GEMINI_API_KEY', '')
print('Key found:', bool(api_key and api_key.strip()))
print('Key prefix:', api_key[:15] if api_key else 'NONE')

payload = {
    "contents": [{
        "parts": [{"text": "Say hello as a pantry chef in one sentence."}]
    }]
}

r = requests.post(
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={api_key}",
    headers={"Content-Type": "application/json"},
    json=payload,
    timeout=25
)

print("Gemini status:", r.status_code)
if r.status_code == 200:
    text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    print("Gemini says:", text.strip())
else:
    print("Error:", r.text[:500])
