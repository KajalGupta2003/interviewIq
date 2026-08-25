from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database import interviews_collection
from models.interview.model import create_interview_doc, interview_schema
from utils.jwtHandler import verify_access_token

router = APIRouter()

# 🔐 JWT Security
security = HTTPBearer()


# ✅ Get current user from token
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return verify_access_token(token)


# ✅ Save Interview (Protected)
@router.post("/save")
def save_interview(data: dict, user=Depends(get_current_user)):
    try:
        #  Override email from token (secure)
        data["user_email"] = user["email"]

        interview = create_interview_doc(data)

        result = interviews_collection.insert_one(interview)
        saved = interviews_collection.find_one({"_id": result.inserted_id})

        return {
            "message": "Interview saved successfully",
            "data": interview_schema(saved)
        }

    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save interview")


# ✅ Get My Interviews (Protected)
@router.get("/my")
def get_my_interviews(user=Depends(get_current_user)):
    try:
        interviews = list(
            interviews_collection.find({"user_email": user["email"]})
            .sort("created_at", -1)  # latest first
        )

        return {
            "count": len(interviews),
            "data": [interview_schema(i) for i in interviews]
        }

    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch interviews")