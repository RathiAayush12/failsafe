"""
FailSafe — ML Inference Service
"""

import pandas as pd
import numpy as np
import joblib
import os
import sys

_ml_path = os.getenv("ML_PIPELINE_PATH", os.path.join(os.path.dirname(__file__), "../../../../ml_pipeline"))
sys.path.insert(0, os.path.abspath(_ml_path))

from explain import SHAPExplainer
from interventions import generate_intervention_plan

MODEL_PATH = os.getenv("MODEL_PATH", "data/model/model.pkl")
FEATURES_PATH = os.getenv("FEATURES_PATH", "data/model/feature_cols.pkl")
SCALER_PATH = os.getenv("SCALER_PATH", "data/processed/scaler.pkl")
ENCODERS_PATH = os.getenv("ENCODERS_PATH", "data/processed/encoders.pkl")


class MLService:
    def __init__(self):
        self.model = None
        self.feature_cols = None
        self.scaler = None
        self.encoders = None
        self.explainer = None
        self._loaded = False

    def load(self):
        if self._loaded:
            return
        try:
            self.model = joblib.load(MODEL_PATH)
            self.feature_cols = joblib.load(FEATURES_PATH)
            self.scaler = joblib.load(SCALER_PATH)
            self.encoders = joblib.load(ENCODERS_PATH)
            self.explainer = SHAPExplainer(self.model, self.feature_cols)
            self._loaded = True
            print("✅ ML model loaded successfully")
        except FileNotFoundError as e:
            print(f"⚠️  Model files not found: {e}")

    def is_ready(self):
        return self._loaded

    def _preprocess_student(self, student_dict: dict):
        from preprocess import engineer_features, encode_features
        df = pd.DataFrame([student_dict])
        df = engineer_features(df)
        df, _ = encode_features(df, self.encoders, fit=False)
        for col in self.feature_cols:
            if col not in df.columns:
                df[col] = 0
        df = df[self.feature_cols]
        df_scaled = pd.DataFrame(self.scaler.transform(df), columns=self.feature_cols)
        return df_scaled, df.iloc[0].to_dict()

    def predict_student(self, student_data: dict, include_shap_chart: bool = True) -> dict:
        if not self._loaded:
            raise RuntimeError("Model not loaded.")
        X_scaled, raw_features = self._preprocess_student(student_data)
        risk_score = float(self.model.predict_proba(X_scaled)[0][1])
        explanation = self.explainer.explain(X_scaled)
        explanation_text = self.explainer.generate_explanation_text(explanation, risk_score)
        shap_chart = self.explainer.plot_waterfall(explanation, student_data.get("name", "Student")) if include_shap_chart else None
        intervention = generate_intervention_plan(raw_features, explanation, risk_score, student_data.get("name", "Student"))
        risk_level = "High" if risk_score >= 0.7 else "Medium" if risk_score >= 0.4 else "Low"
        return {
            "student_id": student_data.get("student_id"),
            "name": student_data.get("name", "Unknown"),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "explanation_text": explanation_text,
            "shap_explanation": explanation,
            "shap_chart_b64": shap_chart,
            "intervention_plan": intervention,
            "raw_features": raw_features,
        }

    def predict_batch(self, students: list, include_shap_chart: bool = False) -> list:
        return [self.predict_student(s, include_shap_chart=include_shap_chart) for s in students]


ml_service = MLService()