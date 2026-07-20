
print("MAIN FILE EXECUTED")
from fastapi.responses import StreamingResponse
from services.voice import text_to_speech
import io
from pydantic import BaseModel
from logger import logger

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import FRONTEND_URL,ALLOWED_DURATIONS
from services.parser import extract_text_from_pdf
from services.resume_extractor import extract_skills, extract_experience, extract_projects, extract_achievements
from services.question_engine import generate_questions, InterviewSession
import services.question_engine
print("Imported from:", generate_questions.__module__)
print("Loaded from:", services.question_engine.__file__)
from services.vision import analyze_frame
from database import db,interviews_collection
from models.user import User
from models.interview import Interview
from bson import ObjectId
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global session (for single user / college demo)
session = None

# --- Endpoints ---

@app.get("/")
def home():
    logger.info("Backend is running")
    return {"message": "InterviewIQ Backend Running"}


@app.post("/save_user")
async def save_user(user: User):

    users_collection = db["users"]

    existing_user = users_collection.find_one({
        "email": user.email
    })

    if existing_user:
        return {
            "message": "User already exists",
            "user_id": str(existing_user["_id"])
        }

    result = users_collection.insert_one({
        "name": user.name,
        "email": user.email,
        "photo": user.photo
    })

    return {
        "message": "User created successfully",
        "user_id": str(result.inserted_id)
    }



@app.post("/save_interview")
async def save_interview(interview: Interview):

    # interviews_collection = db["interviews"]

    result = interviews_collection.insert_one({
        "userEmail": interview.userEmail,
        "role": interview.role,
        "duration": interview.duration,
        "score": interview.score,
        "summary": interview.summary,
        "completedAt": interview.completedAt
    })

    return {
        "message": "Interview saved successfully",
        "interview_id": str(result.inserted_id)
    }



@app.get("/user_interviews/{email}")
async def get_user_interviews(email: str):

    interviews = list(
        interviews_collection.find(
            {"userEmail": email}
        )
    )

    for interview in interviews:
        interview["_id"] = str(interview["_id"])

    return {
        "interviews": interviews
    }

    
@app.get("/interview/{id}")
async def get_interview(id: str):

    interview = interviews_collection.find_one(
        {"_id": ObjectId(id)}
    )

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    interview["_id"] = str(interview["_id"])

    return interview

@app.post("/upload")
async def upload_resume(resume: UploadFile = File(...)):
    if not resume.filename:
        logger.warning("Upload failed: No file selected")
        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )
    if resume.content_type != "application/pdf":
        logger.warning(f"Invalid file type: {resume.content_type}")
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        ) 
   

    await resume.seek(0)
    text = extract_text_from_pdf(resume.file)

    logger.info("Resume parsed successfully")

    skills       = extract_skills(text)
    experience   = extract_experience(text)
    projects     = extract_projects(text)
    achievements = extract_achievements(text)

    return {
        "skills": skills,
        "experience": experience,
        "projects": projects,
        "achievements": achievements
    }


@app.post("/start_interview")
async def start_interview(
    file: UploadFile = File(...),
    role: str = Form(...),
    time: int = Form(...)
):
    global session
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No resume uploaded"
        )

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    if not role.strip():
        raise HTTPException(
            status_code=400,
            detail="Job role cannot be empty"
        )
    if time not in ALLOWED_DURATIONS:
        raise HTTPException(
            status_code=400,
            detail="Duration must be 5, 10, 15 or 20 minutes"
        )  
    logger.info(
    f"Starting interview | Role={role} | Duration={time} min"
    )

    await file.seek(0)

    result = generate_questions(
        pdf_file=file.file,
        job_role=role,
        interview_duration_minutes=time
    )
    logger.info("Questions generated successfully")

    question_bank  = result["questions"]
    resume_context = result["resume_context"]

    # ✅ Guard: check if questions were actually generated
    all_questions = (
        question_bank.get("easy", []) +
        question_bank.get("medium", []) +
        question_bank.get("hard", [])
    )
    if not all_questions:
        raise HTTPException(status_code=500, detail="Failed to generate questions. Please try again.")

    session = InterviewSession(question_bank, time, resume_context)
    logger.info(
    f"Interview session created with {len(session.questions)} questions"
    )

    first_question = session.next_question()

    return {
        "first_question": first_question,
        # "total_questions": result["total"],
        "total_questions": len(session.questions),
        "resume_context": resume_context
    }



@app.post("/submit_answer")
async def submit_answer(data: dict):
    logger.info("Candidate submitted an answer")

    if session is None:
        raise HTTPException(status_code=400, detail="Interview not started")

    score  = session.submit_answer(data["question"], data["answer"])
    logger.info(f"Score object from question_engine: {score}")
    print("Score object:", score)
    next_q = session.next_question()

    if next_q is None:
        logger.info("Interview completed")
        return {
            "score": score,
            "message": "Interview finished",
            "summary": session.interview_summary()
        }

    return {
        "next_question": next_q,
        "score": score
    }


@app.post("/speak")
async def speak(data: dict):
    text = data.get("text")

    if not text:
        raise HTTPException(status_code=400, detail="No text provided")

    audio_bytes = text_to_speech(text)

    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type="audio/mpeg"
    )

class AnalysisRequest(BaseModel):
    image: str

@app.post("/analyze")
async def analyze_camera(data: AnalysisRequest):
    result = analyze_frame(data.image)
    return {
        "eye_contact": result["eye_contact"],
        "blink":       result["blink"],
        "status":      "success"
    }