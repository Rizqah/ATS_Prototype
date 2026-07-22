"""Request and response schemas for the TrueFit API."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Credentials(BaseModel):
    email: str
    password: str = Field(min_length=1)
    otp_code: Optional[str] = None
    role: Optional[str] = None
    full_name: Optional[str] = None
    job_title: Optional[str] = None


class UserUpdate(BaseModel):
    data: Dict[str, Any]


class ProfileUpdate(BaseModel):
    data: Dict[str, Any]


class ExperienceCreate(BaseModel):
    company: str = Field(min_length=1)
    position: str = Field(min_length=1)
    start_date: str = ""
    end_date: str = ""
    current_job: bool = False
    description: str = ""


class ExperienceUpdate(BaseModel):
    data: Dict[str, Any]


class SkillCreate(BaseModel):
    skill_name: str = Field(min_length=1)
    proficiency: str = "Intermediate"


class SkillUpdate(BaseModel):
    data: Dict[str, Any]


class AchievementCreate(BaseModel):
    achievement: str = Field(min_length=1)
    metric: str = ""


class CandidateResume(BaseModel):
    name: str
    resume: str
    candidate_name: Optional[str] = None


class BatchMatchRequest(BaseModel):
    job_description: str = Field(min_length=1)
    candidates: List[CandidateResume]


class ProfileMatchRequest(BaseModel):
    profile: Dict[str, Any]
    work_experiences: List[Dict[str, Any]] = Field(default_factory=list)
    achievements_by_experience: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    skills: List[Dict[str, Any]] = Field(default_factory=list)
    job_description: str = Field(min_length=1)


class FeedbackRequest(BaseModel):
    job_description: str = Field(min_length=1)
    candidate_resume: str = Field(min_length=1)
    candidate_name: Optional[str] = None
    recruiter_name: Optional[str] = None
    recruiter_job_title: Optional[str] = None


class CVRequest(BaseModel):
    profile: Dict[str, Any]
    work_experiences: List[Dict[str, Any]] = Field(default_factory=list)
    achievements_by_experience: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    skills: List[Dict[str, Any]] = Field(default_factory=list)
    job_description: Optional[str] = None


class CVOptimizeRequest(CVRequest):
    job_description: str = Field(min_length=1)


class CVStatusUpdate(BaseModel):
    status: str = Field(min_length=1)


class CVHistoryCreate(BaseModel):
    job_title: str = Field(min_length=1)
    match_score: float = 0
    cv_content: str = ""
    job_description: str = Field(min_length=1)


class PasswordChangeRequest(BaseModel):
    email: str
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8)


class PasswordResetRequest(BaseModel):
    email: str


class PasswordResetConfirm(BaseModel):
    email: str
    token: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8)


class TwoFactorConfirm(BaseModel):
    email: str
    code: str = Field(min_length=6)


class TwoFactorDisable(BaseModel):
    email: str
    password: str = Field(min_length=1)
    code: str = Field(min_length=6)


class AccountDeleteRequest(BaseModel):
    email: str
    password: str = Field(min_length=1)
    confirmation: str


class RecruiterWorkspaceUpdate(BaseModel):
    workspace: Dict[str, Any]


class EmailSendRequest(BaseModel):
    recruiter_email: str
    to_email: str
    subject: str = Field(min_length=1)
    body: str = Field(min_length=1)
