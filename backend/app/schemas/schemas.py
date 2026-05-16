"""
FailSafe — Pydantic Schemas
Request/response validation
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# ─── Auth ────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "faculty"
    department: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    department: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ─── Student Input ────────────────────────────────────────────────────────────

class StudentFeatures(BaseModel):
    student_id: Optional[str] = None
    name: Optional[str] = "Unknown"
    school: str = "GP"
    sex: str = "M"
    age: int = 17
    address: str = "U"
    famsize: str = "GT3"
    Pstatus: str = "T"
    Medu: int = 2
    Fedu: int = 2
    Mjob: str = "other"
    Fjob: str = "other"
    reason: str = "course"
    guardian: str = "mother"
    traveltime: int = 2
    studytime: int = 2
    failures: int = 0
    schoolsup: str = "no"
    famsup: str = "yes"
    paid: str = "no"
    activities: str = "no"
    nursery: str = "yes"
    higher: str = "yes"
    internet: str = "yes"
    romantic: str = "no"
    famrel: int = 4
    freetime: int = 3
    goout: int = 3
    Dalc: int = 1
    Walc: int = 1
    health: int = 3
    absences: int = 0
    G1: Optional[int] = None
    G2: Optional[int] = None


class PredictRequest(BaseModel):
    students: List[StudentFeatures]


# ─── Prediction Response ──────────────────────────────────────────────────────

class SHAPContribution(BaseModel):
    feature: str
    description: str
    shap_value: float
    feature_value: float
    direction: str


class SHAPExplanation(BaseModel):
    expected_value: float
    contributions: List[SHAPContribution]
    top_risk_factors: List[SHAPContribution]
    top_protective_factors: List[SHAPContribution]


class InterventionAction(BaseModel):
    category: str
    priority: str
    action: str
    followup: str


class InterventionPlan(BaseModel):
    student_name: str
    risk_score: float
    risk_level: str
    summary: str
    interventions: List[InterventionAction]
    total_actions: int


class PredictionResult(BaseModel):
    student_id: Optional[str]
    name: str
    risk_score: float
    risk_level: str
    explanation_text: str
    shap_explanation: SHAPExplanation
    shap_chart_b64: Optional[str] = None
    intervention_plan: InterventionPlan
    raw_features: Optional[Dict[str, Any]] = None


class PredictResponse(BaseModel):
    results: List[PredictionResult]
    total: int
    at_risk_count: int
    upload_id: Optional[int] = None


# ─── Dashboard ────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_students: int
    at_risk_high: int
    at_risk_medium: int
    at_risk_low: int
    interventions_pending: int
    interventions_in_progress: int
    interventions_completed: int
    recent_uploads: int


class InterventionUpdate(BaseModel):
    status: Optional[str] = None
    faculty_notes: Optional[str] = None


class InterventionOut(BaseModel):
    id: int
    prediction_id: int
    student_name: str
    risk_level: str
    summary: str
    actions: List[Dict[str, Any]]
    status: str
    faculty_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
