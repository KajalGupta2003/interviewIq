from datetime import datetime, timezone

def create_interview_doc(data):
    return {
        "user_email": data.get("user_email"),  # later replace with user_id
        
        # Core interview data
        "score": data.get("score"),
        "questions": data.get("questions", []),
        "answers": data.get("answers", []),

        #  Timer data
        "duration": data.get("duration"),  # in seconds
        "started_at": data.get("started_at"),  # optional (frontend send)
        "ended_at": data.get("ended_at"),      # optional

        #  Camera / AI metrics
        "confidence_score": data.get("confidence_score"),  # overall confidence
        "eye_contact_score": data.get("eye_contact_score"),
        "blink_rate": data.get("blink_rate"),
        "face_detected": data.get("face_detected", True),

        #  AI feedback
        "feedback": data.get("feedback"),

        # System timestamp
        "created_at": datetime.now(timezone.utc)
    }


def interview_schema(interview):
    return {
        "id": str(interview["_id"]),
        "user_email": interview.get("user_email"),

        # Core data
        "score": interview.get("score"),
        "questions": interview.get("questions", []),
        "answers": interview.get("answers", []),

        # Timer
        "duration": interview.get("duration"),
        "started_at": interview.get("started_at"),
        "ended_at": interview.get("ended_at"),

        # Camera metrics
        "confidence_score": interview.get("confidence_score"),
        "eye_contact_score": interview.get("eye_contact_score"),
        "blink_rate": interview.get("blink_rate"),
        "face_detected": interview.get("face_detected"),

        # Feedback
        "feedback": interview.get("feedback"),

        # Timestamp (JSON safe)
        "created_at": interview.get("created_at").isoformat() if interview.get("created_at") else None
    }