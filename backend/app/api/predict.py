"""
FailSafe — Predict Routes
CSV upload and per-student prediction
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.models import User, Student, Prediction, Intervention, Upload
from app.schemas.schemas import PredictRequest, PredictResponse, PredictionResult
from app.services.auth import get_current_user
from app.services.ml_service import ml_service
import pandas as pd
import io
import json

router = APIRouter(prefix="/api/predict", tags=["predict"])


@router.post("/", response_model=PredictResponse)
def predict(
    request: PredictRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not ml_service.is_ready():
        raise HTTPException(status_code=503, detail="ML model not loaded. Contact administrator.")

    students_data = [s.model_dump() for s in request.students]
    results_raw = ml_service.predict_batch(students_data)

    results = []
    for raw in results_raw:
        # Upsert student
        student_id = raw.get("student_id") or f"STU_{raw['name'].replace(' ', '_')}"
        db_student = db.query(Student).filter(Student.student_id == student_id).first()
        if not db_student:
            db_student = Student(
                student_id=student_id,
                name=raw["name"],
                faculty_id=current_user.id,
            )
            db.add(db_student)
            db.flush()

        # Save prediction
        pred = Prediction(
            student_id=db_student.id,
            risk_score=raw["risk_score"],
            risk_level=raw["risk_level"],
            shap_values=raw["shap_explanation"]["contributions"][:10],
            explanation_text=raw["explanation_text"],
            raw_features=raw.get("raw_features", {}),
        )
        db.add(pred)
        db.flush()

        # Save intervention
        plan = raw["intervention_plan"]
        interv = Intervention(
            prediction_id=pred.id,
            student_name=plan["student_name"],
            risk_level=plan["risk_level"],
            summary=plan["summary"],
            actions=plan["interventions"],
            status="pending",
        )
        db.add(interv)
        results.append(PredictionResult(**raw))

    db.commit()

    at_risk = sum(1 for r in results if r.risk_level in ("High", "Medium"))
    return PredictResponse(
        results=results,
        total=len(results),
        at_risk_count=at_risk
    )


@router.post("/upload-csv", response_model=PredictResponse)
async def predict_from_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    contents = await file.read()
    try:
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")), sep=None, engine="python")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {e}")

    students = df.to_dict(orient="records")
    if not students:
        raise HTTPException(status_code=400, detail="CSV is empty.")

    if not ml_service.is_ready():
        raise HTTPException(status_code=503, detail="ML model not loaded.")

    results_raw = ml_service.predict_batch(students)

    upload = Upload(
        filename=file.filename,
        uploader_id=current_user.id,
        record_count=len(students),
        at_risk_count=sum(1 for r in results_raw if r["risk_level"] in ("High", "Medium")),
    )
    db.add(upload)
    db.flush()

    results = []
    for raw in results_raw:
        student_id = raw.get("student_id") or f"STU_{raw['name'].replace(' ', '_')}"
        db_student = db.query(Student).filter(Student.student_id == student_id).first()
        if not db_student:
            db_student = Student(
                student_id=student_id,
                name=raw["name"],
                faculty_id=current_user.id,
            )
            db.add(db_student)
            db.flush()

        pred = Prediction(
            student_id=db_student.id,
            risk_score=raw["risk_score"],
            risk_level=raw["risk_level"],
            shap_values=raw["shap_explanation"]["contributions"][:10],
            explanation_text=raw["explanation_text"],
            raw_features=raw.get("raw_features", {}),
            upload_id=upload.id,
        )
        db.add(pred)
        db.flush()

        plan = raw["intervention_plan"]
        interv = Intervention(
            prediction_id=pred.id,
            student_name=plan["student_name"],
            risk_level=plan["risk_level"],
            summary=plan["summary"],
            actions=plan["interventions"],
            status="pending",
        )
        db.add(interv)
        results.append(PredictionResult(**raw))

    db.commit()

    at_risk = sum(1 for r in results if r.risk_level in ("High", "Medium"))
    return PredictResponse(
        results=results,
        total=len(results),
        at_risk_count=at_risk,
        upload_id=upload.id,
    )
