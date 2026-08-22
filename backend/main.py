from dotenv import load_dotenv
load_dotenv()
from fastapi.responses import StreamingResponse
from services.voice import text_to_speech
import io
from pydantic import BaseModel

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from services.parser import extract_text_from_pdf
from services.resume_extractor import extract_skills, extract_experience, extract_projects, extract_achievements
from services.question_engine import generate_questions, InterviewSession
from services.vision import analyze_frame
from routes import auth
from routes import interview
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global session (for single user / college demo)
session = None

# --- Endpoints ---

@app.get("/")
def home():
    return {"message": "InterviewIQ Backend Running"}


@app.post("/upload")
async def upload_resume(resume: UploadFile = File(...)):
    await resume.seek(0)
    text = extract_text_from_pdf(resume.file)

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

    await file.seek(0)

    result = generate_questions(
        pdf_file=file.file,
        job_role=role,
        interview_duration_minutes=time
    )

    question_bank  = result["questions"]
    resume_context = result["resume_context"]

    #  Guard: check if questions were actually generated
    all_questions = (
        question_bank.get("easy", []) +
        question_bank.get("medium", []) +
        question_bank.get("hard", [])
    )
    if not all_questions:
        raise HTTPException(status_code=500, detail="Failed to generate questions. Please try again.")

    session = InterviewSession(question_bank, time, resume_context)
    first_question = session.next_question()

    return {
        "first_question": first_question,
        # "total_questions": result["total"],
        "total_questions": len(session.questions),
        "resume_context": resume_context
    }



@app.post("/submit_answer")
async def submit_answer(data: dict):
    if session is None:
        raise HTTPException(status_code=400, detail="Interview not started")

    score  = session.submit_answer(data["question"], data["answer"])
    next_q = session.next_question()

    if next_q is None:
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
app.include_router(auth.router, prefix="/auth")
app.include_router(interview.router, prefix="/interview")