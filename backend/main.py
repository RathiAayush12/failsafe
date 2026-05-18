"""
FailSafe — FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.models.database import create_tables, SessionLocal
from app.models.models import User
from app.services.auth import get_password_hash
from app.services.ml_service import ml_service
from app.api.auth import router as auth_router
from app.api.predict import router as predict_router
from app.api.dashboard import router as dashboard_router, interventions_router


def seed_demo_user():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "admin@failsafe.edu").first()
        if not user:
            new_user = User(
                email="admin@failsafe.edu",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin Faculty",
                role="hod"
            )
            db.add(new_user)
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    seed_demo_user()
    ml_service.load()
    yield
    # Shutdown (cleanup if needed)


app = FastAPI(
    title="FailSafe API",
    description="Early student failure detection with Explainable AI",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(predict_router)
app.include_router(dashboard_router)
app.include_router(interventions_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": ml_service.is_ready(),
    }
