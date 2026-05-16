"""
FailSafe — ML Pipeline Tests
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../ml_pipeline"))


def test_engineer_features():
    from preprocess import engineer_features

    df = pd.DataFrame([{
        "G1": 10, "G2": 12, "G3": 8,
        "absences": 12, "studytime": 1, "failures": 1,
        "Dalc": 2, "Walc": 3,
    }])
    result = engineer_features(df)
    assert "at_risk" in result.columns
    assert result["at_risk"].iloc[0] == 1  # G3=8 < 10 → at risk
    assert "grade_trend" in result.columns
    assert result["grade_trend"].iloc[0] == -2  # 8 - 10
    assert "alcohol_index" in result.columns
    assert "absence_level" in result.columns


def test_intervention_generation():
    from interventions import generate_intervention_plan

    student = {"absences": 20, "failures": 2, "studytime": 1, "health": 2}
    explanation = {"top_risk_factors": [], "top_protective_factors": []}

    plan = generate_intervention_plan(student, explanation, 0.85, "Test Student")

    assert plan["risk_level"] == "High"
    assert plan["total_actions"] > 0
    assert any(i["category"] == "Attendance" for i in plan["interventions"])
    assert any(i["priority"] == "High" for i in plan["interventions"])


def test_intervention_low_risk():
    from interventions import generate_intervention_plan

    student = {"absences": 1, "failures": 0, "studytime": 3, "health": 4}
    explanation = {"top_risk_factors": [], "top_protective_factors": []}
    plan = generate_intervention_plan(student, explanation, 0.15, "Good Student")

    assert plan["risk_level"] == "Low"


def test_shap_explainer_mock():
    """Test SHAP explainer structure without a real model."""
    from explain import FEATURE_DESCRIPTIONS

    assert "absences" in FEATURE_DESCRIPTIONS
    assert "failures" in FEATURE_DESCRIPTIONS
    assert "studytime" in FEATURE_DESCRIPTIONS
