from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Interview(BaseModel):
    userEmail: str
    role: str
    duration: int
    score: float
    summary: dict
    completedAt: Optional[datetime] = datetime.utcnow()