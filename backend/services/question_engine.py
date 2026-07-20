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
    if interview_duration_minutes <= 5:
        num_questions = 4
    elif interview_duration_minutes <= 10:
        num_questions = 6
    elif interview_duration_minutes <= 15:
        num_questions = 8
    else:
        num_questions = 10
    easy_count    = max(1, num_questions // 3)
    medium_count  = max(1, num_questions // 3)
    hard_count    = num_questions - easy_count - medium_count

    resume_context = build_resume_context(pdf_file)

    prompt = f"""
You are an experienced Senior Technical Interviewer at a top product-based company.

Candidate Resume:
{resume_context}

Target Job Role:
{job_role}

Interview Duration:
{interview_duration_minutes} minutes

Generate exactly {num_questions} interview questions.

Difficulty Distribution:
- Easy: {easy_count}
- Medium: {medium_count}
- Hard: {hard_count}

IMPORTANT RULES:

1. Questions must primarily evaluate the candidate for the role "{job_role}".

2. Use the resume only to personalize the interview.
If the resume mentions specific technologies, projects, internships or achievements, include questions related to them.

3. Around 60% of the questions should be based on the candidate's resume.

4. Around 40% should test role-specific concepts that may not be present in the resume.

5. Choose questions from DIFFERENT topics.
Do NOT ask multiple questions from the same concept.

6. Include a healthy mix of:
- Theory
- Practical implementation
- Project discussion
- Debugging
- Real-world scenarios
- Best practices

7. Do NOT generate generic HR questions like:
- Tell me about yourself
- Why should we hire you?
- What are your strengths?

8. Every question must be unique.

9. Avoid repetitive wording.

10. Questions should become gradually harder.

11. Keep each question under 35 words.

12. Ask questions exactly like a real interviewer.
13. Never repeat a question that tests the same underlying concept.
For example, if one question asks about React Hooks,
do not ask another question about useEffect or useState unless it explores a completely different real-world scenario.

Return ONLY valid JSON.

{{
    "easy":[...],
    "medium":[...],
    "hard":[...]
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
            if not isinstance(questions.get(key), list):
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
You are an experienced Senior Technical Interviewer evaluating a candidate fairly and consistently.

Resume Context:
{self.resume_context}

Interview Question:
{question}

Candidate Answer:
{answer}

Evaluate the answer based on:
- Technical accuracy
- Understanding of concepts
- Practical knowledge
- Communication clarity
- Completeness of the answer

IMPORTANT SCORING GUIDELINES:

- 9-10:
  Complete, technically accurate, well explained, demonstrates deep understanding.

- 7-8:
  Good answer with correct concepts. Minor details may be missing but overall interview-worthy.

- 5-6:
  Average fresher-level answer. Candidate understands the topic but explanation is incomplete or lacks depth.

- 3-4:
  Weak answer. Candidate knows only small parts of the topic or has significant gaps.

- 0-2:
  Completely incorrect answer, irrelevant answer, or no meaningful technical understanding.

IMPORTANT:

- DO NOT be overly strict.
- If the candidate shows partial understanding, NEVER give below 5 unless the answer is mostly incorrect.
- Ignore grammar mistakes.
- Ignore pronunciation mistakes.
- Focus only on technical understanding.
- Reward practical examples when present.
- If the candidate gives a correct answer but misses some details,
reward the correct understanding instead of penalizing heavily.

Feedback Rules:

- Feedback should be constructive.
- Mention what was good.
- Mention what can be improved.
- Never insult the candidate.

Strengths:
Return 2-3 short bullet points.

Weaknesses:
Return 2-3 short bullet points.

Missed Points:
Return the important concepts that were not mentioned.

Ideal Answer:
Provide a concise model interview answer (maximum 120 words).

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

            try:
                 score = float(result.get("score", 0))
            except:
                score = 0

            score = max(0, min(10, round(score, 1)))
            feedback = str(result.get("feedback", ""))
            strengths = result.get("strengths", [])
            if not isinstance(strengths, list):
                strengths = [str(strengths)]
            weaknesses = result.get("weaknesses", [])
            if not isinstance(weaknesses, list):
                weaknesses = [str(weaknesses)]

            missed = result.get("missed_points", [])
            if not isinstance(missed, list):
                missed = [str(missed)]
            ideal_answer = str(result.get("ideal_answer", ""))

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