from datetime import datetime, timezone

def create_user_doc(data):
    return {
        "name": data.get("name"),
        "email": data.get("email"),
        "picture": data.get("picture"),
        "created_at": datetime.now(timezone.utc)  
    }

def user_schema(user):
    return {
        "id": str(user["_id"]),
        "name": user.get("name"),
        "email": user.get("email"),
        "picture": user.get("picture"),
        "created_at": user.get("created_at").isoformat() if user.get("created_at") else None
    }