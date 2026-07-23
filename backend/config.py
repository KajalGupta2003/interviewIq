import os 
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY=os.getenv("GROQ_API_KEY")
ELEVEN_API_KEY=os.getenv("ElEVEN_API_KEY")

FRONTEND_URL=os.getenv("FRONTEND_URL","http://localhost:5173")
VOICE_ID = os.getenv(
    "VOICE_ID",
    "ImyAQXVPmdjA0EnqOdjw"
)
ALLOWED_DURATIONS=[5,10,15,20]
MONGODB_URI = os.getenv("MONGODB_URI")
MAX_PDF_SIZE=5*1024*1024