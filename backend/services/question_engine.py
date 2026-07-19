print("QUESTION ENGINE EXECUTED")
import json

from groq import Groq
from logger import logger
from services.parser import extract_text_from_pdf
from services.resume_extractor import (
    extract_skills,
    extract_experience,
    extract_projects,
    extract_achievements
)

from config import GROQ_API_KEY
print("========== NEW QUESTION_ENGINE FILE LOADED ==========")
client = Groq(api_key=GROQ_API_KEY)

def call_llm(prompt: str) -> str:
    logger.info("Sending request to Groq...")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    logger.info("Groq response received successfully")
    return response.choices[0].message.content


# ── 1. Resume Context Builder ─────────────────────────────────────────────────

def build_resume_context(pdf_file):
    raw_text = extract_text_from_pdf(pdf_file)

    skills       = extract_skills(raw_text)
    experience   = extract_experience(raw_text)
    projects     = extract_projects(raw_text)
    achievements = extract_achievements(raw_text)

    context = f"""
SKILLS:
{", ".join(skills) if skills else "Not found"}

EXPERIENCE:
{chr(10).join(experience) if experience else "Not found"}

PROJECTS:
{chr(10).join(projects) if projects else "Not found"}

ACHIEVEMENTS:
{chr(10).join(achievements) if achievements else "Not found"}
"""
    return context.strip()


# ── 2. Question Generator ─────────────────────────────────────────────────────

def generate_questions(pdf_file, job_role, interview_duration_minutes):
    num_questions = max(3, interview_duration_minutes // 2)
    easy_count    = max(1, num_questions // 3)
    medium_count  = max(1, num_questions // 3)
    hard_count    = num_questions - easy_count - medium_count

    resume_context = build_resume_context(pdf_file)

    prompt = f"""
You are a professional HR interviewer conducting a technical interview.

Candidate Resume:
{resume_context}

Target Job Role: {job_role}
Interview Duration: {interview_duration_minutes} minutes
Total Questions Needed: {num_questions} ({easy_count} easy, {medium_count} medium, {hard_count} hard)

Generate exactly {num_questions} interview questions strictly based on the candidate's
resume and the target job role. Questions should feel like a real HR interview.

Rules:
- Easy: Basic questions about listed skills and background
- Medium: Situational or project-based questions from their experience
- Hard: Deep technical or problem-solving questions challenging their expertise

Return ONLY valid JSON, no explanation, no markdown:
{{
  "easy": ["question1", "question2"],
  "medium": ["question1", "question2"],
  "hard": ["question1", "question2"]
}}
"""

    try:
        text = call_llm(prompt)

        logger.info(f"Raw Groq Response:\n{text}")
        print("Raw Groq Response:\n", text)
        text = text.replace("```json", "").replace("```", "").strip()

        start = text.find("{")
        end   = text.rfind("}") + 1
        text  = text[start:end]

        questions = json.loads(text)

        for key in ["easy", "medium", "hard"]:
            if key not in questions:
                questions[key] = []

        # Hard cap to exact counts
        return {
            "questions": {
                "easy":   questions["easy"][:easy_count],
                "medium": questions["medium"][:medium_count],
                "hard":   questions["hard"][:hard_count],
            },
            "total": num_questions,
            "resume_context": resume_context
        }

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        logger.error(f"Question JSON parse error: {e}")
        return {"questions": {"easy": [], "medium": [], "hard": []}, "total": 0, "resume_context": ""}

    except Exception as e:
        print(f"Groq error: {e}")
        raise


# ── 3. Interview Session ──────────────────────────────────────────────────────

class InterviewSession:
    def __init__(self, question_bank: dict, duration_minutes: int, resume_context: str):
        self.resume_context   = resume_context
        self.duration_minutes = duration_minutes
        self.scores           = []
        self.answered         = []

        self.questions = (
            question_bank.get("easy",   []) +
            question_bank.get("medium", []) +
            question_bank.get("hard",   [])
        )
        self.current_index = 0

    def next_question(self):
        if self.current_index < len(self.questions):
            q = self.questions[self.current_index]
            self.current_index += 1
            return q
        return None

    def submit_answer(self, question: str, answer: str) -> dict:
        prompt = f"""
You are a strict but fair HR interviewer evaluating a candidate's answer.

Resume Context:
{self.resume_context}

Interview Question:
{question}

Candidate's Answer:
{answer}

Evaluate the candidate objectively.

Scoring Rules:
- 9-10 = Excellent
- 7-8 = Good
- 5-6 = Average
- 3-4 = Weak
- 0-2 = Incorrect

Return ONLY valid JSON.

{{
    "score": 0,
    "feedback": "",
    "strengths": [],
    "weaknesses": [],
    "missed_points": [],
    "ideal_answer": ""
}}
"""
        try:
            text = call_llm(prompt)
            text = text.replace("```json", "").replace("```", "").strip()

            start = text.find("{")
            end   = text.rfind("}") + 1
            text  = text[start:end]

            result = json.loads(text)
            print("========== RAW LLM RESPONSE ==========")
            print(text)

            print("========== PARSED RESULT ==========")
            print(result)
            logger.info(f"Parsed JSON:\n{result}")
            print("Parsed JSON:\n", result)

            score = result.get("score", 0)
            feedback = result.get("feedback", "")
            strengths = result.get("strengths", [])
            weaknesses = result.get("weaknesses", [])
            missed = result.get("missed_points", [])
            ideal_answer = result.get("ideal_answer", "")

        except Exception as e:
            print(f"Evaluation error: {e}")

            score = 0
            feedback = "Could not evaluate answer."
            strengths = []
            weaknesses = []
            missed = []
            ideal_answer = ""

        self.scores.append(score)
        self.answered.append({
            "question":      question,
            "answer":        answer,
            "score":         score,
            "feedback":      feedback,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "missed_points": missed,
            "ideal_answer": ideal_answer
        })

        response = {
            "score": score,
            "feedback": feedback,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "missed_points": missed,
            "ideal_answer": ideal_answer
        }

        logger.info(f"Returning Response:\n{response}")
        print("Returning Response:\n", response)

        return response
    def interview_summary(self) -> dict:
        if not self.scores:
            return {"average_score": 0, "total_questions": 0, "details": []}

        avg = round(sum(self.scores) / len(self.scores), 2)

        if avg >= 8:
            performance = "Excellent"
        elif avg >= 6:
            performance = "Good"
        elif avg >= 4:
            performance = "Average"
        else:
            performance = "Needs Improvement"

        return {
            "average_score":   avg,
            "performance":     performance,
            "total_questions": len(self.scores),
            "details":         self.answered
        }