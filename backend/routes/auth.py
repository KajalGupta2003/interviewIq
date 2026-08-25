from fastapi import APIRouter, HTTPException
from db.mongo import users_collection
from models.user import create_user_doc, user_schema
from services.google_auth import verify_google_token
from utils.jwtHandler import create_access_token

router = APIRouter()


@router.post("/google-login")
def google_login(token: str):
    try:
        # 🔐 Verify Google token
        user_data = verify_google_token(token)

        # 🔎 Check if user exists
        existing_user = users_collection.find_one({"email": user_data["email"]})

        if existing_user:
            user = existing_user
            message = "User exists"
        else:
            # 🆕 Create new user
            new_user = create_user_doc(user_data)
            result = users_collection.insert_one(new_user)
            user = users_collection.find_one({"_id": result.inserted_id})
            message = "User created"

        # 🔑 Generate JWT
        access_token = create_access_token({
            "email": user["email"]
        })

        return {
            "message": message,
            "user": user_schema(user),
            "access_token": access_token
        }

    except Exception as e:
        print("AUTH ERROR:", e)   # 👈 IMPORTANT DEBUG
        raise HTTPException(status_code=401, detail="Google login failed")