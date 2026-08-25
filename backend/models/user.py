from pydantic import BaseModel, EmailStr
from typing import Optional


class User(BaseModel):
    name: str
    email: EmailStr
    photo: Optional[str] = None


def create_user_doc(user_data: dict):
    return {
        "name": user_data["name"],
        "email": user_data["email"],
        "photo": user_data.get("photo") or user_data.get("picture"),
    }


def user_schema(user: dict):
    return {
        "name": user.get("name"),
        "email": user.get("email"),
        "photo": user.get("photo"),
    }