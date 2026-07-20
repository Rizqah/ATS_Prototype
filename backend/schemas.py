"""Request and response schemas for the TrueFit API."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Credentials(BaseModel):
    email: str
    password: str = Field(min_length=1)


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


class CVRequest(BaseModel):
    profile: Dict[str, Any]
    work_experiences: List[Dict[str, Any]] = Field(default_factory=list)
    achievements_by_experience: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    skills: List[Dict[str, Any]] = Field(default_factory=list)
    job_description: Optional[str] = None


class CVOptimizeRequest(CVRequest):
    job_description: str = Field(min_length=1)
