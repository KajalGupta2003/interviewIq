from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import HTTPException
import os

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

print("CLIENT_ID:", GOOGLE_CLIENT_ID)
def verify_google_token(token: str):
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        return {
            "email": idinfo.get("email"),
            "name": idinfo.get("name"),
            "picture": idinfo.get("picture")
        }

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Google token")