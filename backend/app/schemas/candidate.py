from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class CandidateCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=255)


class CandidateRead(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime


class CandidateProfileResponse(BaseModel):
    candidate: CandidateRead
    aggregate_score: float | None = None
    raw_scores: dict[str, float] = {}
    normalized_scores: dict[str, float] = {}
