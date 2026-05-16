"""
FailSafe — Dashboard & Interventions Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.database import get_db
from app.models.models import User, Student, Prediction, Intervention, Upload
from app.schemas.schemas import (
    DashboardStats, InterventionUpdate, InterventionOut
)
from app.services.auth import get_current_user, require_role
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])
interventions_router = APIRouter(prefix="/api/interventions", tags=["interventions"])


@router.get("/stats", response_model=DashboardStats)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # HODs see all; faculty see only their students
    if current_user.role in ("hod", "admin"):
        students_q = db.query(Student)
        predictions_q = db.query(Prediction)
        interventions_q = db.query(Intervention)
    else:
        students_q = db.query(Student).filter(Student.faculty_id == current_user.id)
        student_ids = [s.id for s in students_q.all()]
        predictions_q = db.query(Prediction).filter(Prediction.student_id.in_(student_ids))
        pred_ids = [p.id for p in predictions_q.all()]
        interventions_q = db.query(Intervention).filter(Intervention.prediction_id.in_(pred_ids))

    total_students = students_q.count()
    recent = datetime.utcnow() - timedelta(days=30)

    high = predictions_q.filter(Prediction.risk_level == "High").count()
    medium = predictions_q.filter(Prediction.risk_level == "Medium").count()
    low = predictions_q.filter(Prediction.risk_level == "Low").count()

    pending = interventions_q.filter(Intervention.status == "pending").count()
    in_progress = interventions_q.filter(Intervention.status == "in_progress").count()
    completed = interventions_q.filter(Intervention.status == "completed").count()

    recent_uploads = db.query(Upload).filter(
        Upload.uploaded_at >= recent,
        Upload.uploader_id == current_user.id
    ).count()

    return DashboardStats(
        total_students=total_students,
        at_risk_high=high,
        at_risk_medium=medium,
        at_risk_low=low,
        interventions_pending=pending,
        interventions_in_progress=in_progress,
        interventions_completed=completed,
        recent_uploads=recent_uploads,
    )


@router.get("/students")
def get_students(
    risk_level: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role in ("hod", "admin"):
        students = db.query(Student).all()
    else:
        students = db.query(Student).filter(Student.faculty_id == current_user.id).all()

    result = []
    for s in students:
        latest_pred = (
            db.query(Prediction)
            .filter(Prediction.student_id == s.id)
            .order_by(Prediction.predicted_at.desc())
            .first()
        )
        if latest_pred:
            if risk_level and latest_pred.risk_level != risk_level:
                continue
            interv = db.query(Intervention).filter(
                Intervention.prediction_id == latest_pred.id
            ).first()
            result.append({
                "id": s.id,
                "student_id": s.student_id,
                "name": s.name,
                "risk_score": round(latest_pred.risk_score, 3),
                "risk_level": latest_pred.risk_level,
                "explanation_text": latest_pred.explanation_text,
                "predicted_at": latest_pred.predicted_at,
                "intervention_status": interv.status if interv else None,
            })

    result.sort(key=lambda x: x["risk_score"], reverse=True)
    return result


@router.get("/student/{student_id}")
def get_student_detail(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    predictions = (
        db.query(Prediction)
        .filter(Prediction.student_id == student.id)
        .order_by(Prediction.predicted_at.desc())
        .all()
    )

    pred_list = []
    for p in predictions:
        interv = db.query(Intervention).filter(Intervention.prediction_id == p.id).first()
        pred_list.append({
            "id": p.id,
            "risk_score": p.risk_score,
            "risk_level": p.risk_level,
            "explanation_text": p.explanation_text,
            "shap_values": p.shap_values,
            "predicted_at": p.predicted_at,
            "intervention": {
                "id": interv.id,
                "status": interv.status,
                "summary": interv.summary,
                "actions": interv.actions,
                "faculty_notes": interv.faculty_notes,
            } if interv else None,
        })

    return {
        "student": {
            "id": student.id,
            "student_id": student.student_id,
            "name": student.name,
        },
        "predictions": pred_list,
    }


# ─── Interventions ────────────────────────────────────────────────────────────

@interventions_router.get("/", response_model=List[InterventionOut])
def list_interventions(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Intervention)
    if status:
        q = q.filter(Intervention.status == status)
    return q.order_by(Intervention.created_at.desc()).all()


@interventions_router.patch("/{intervention_id}", response_model=InterventionOut)
def update_intervention(
    intervention_id: int,
    update: InterventionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    interv = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if not interv:
        raise HTTPException(status_code=404, detail="Intervention not found")

    if update.status:
        interv.status = update.status
    if update.faculty_notes is not None:
        interv.faculty_notes = update.faculty_notes

    db.commit()
    db.refresh(interv)
    return interv
