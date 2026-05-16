"""
FailSafe — SQLAlchemy Database Models
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="faculty")  # faculty | hod | admin
    department = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    students = relationship("Student", back_populates="faculty")
    uploads = relationship("Upload", back_populates="uploader")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True)
    name = Column(String)
    age = Column(Integer)
    sex = Column(String)
    school = Column(String)
    faculty_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    faculty = relationship("User", back_populates="students")
    predictions = relationship("Prediction", back_populates="student")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    risk_score = Column(Float)
    risk_level = Column(String)  # High | Medium | Low
    shap_values = Column(JSON)
    explanation_text = Column(Text)
    raw_features = Column(JSON)
    predicted_at = Column(DateTime, default=datetime.utcnow)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=True)

    student = relationship("Student", back_populates="predictions")
    intervention = relationship("Intervention", back_populates="prediction", uselist=False)
    upload = relationship("Upload", back_populates="predictions")


class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), unique=True)
    student_name = Column(String)
    risk_level = Column(String)
    summary = Column(Text)
    actions = Column(JSON)
    status = Column(String, default="pending")  # pending | in_progress | completed
    faculty_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    prediction = relationship("Prediction", back_populates="intervention")


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    uploader_id = Column(Integer, ForeignKey("users.id"))
    record_count = Column(Integer)
    at_risk_count = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    uploader = relationship("User", back_populates="uploads")
    predictions = relationship("Prediction", back_populates="upload")
