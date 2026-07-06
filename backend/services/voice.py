import requests

from config import ELEVEN_API_KEY,VOICE_ID





def text_to_speech(text: str) -> bytes:
    if not ELEVEN_API_KEY:
        raise Exception("API key not loaded. Check .env")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",  # safe model
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.7
        }
    }

    response = requests.post(url, json=data, headers=headers)

    # 🔥 Debug (keep for now)
    print("STATUS:", response.status_code)
    # print("RESPONSE:", response.text[:200])

    if response.status_code != 200:
        raise Exception(f"ElevenLabs error: {response.text}")

    return response.content