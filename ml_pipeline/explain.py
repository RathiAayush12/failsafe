"""
FailSafe — SHAP Explainability
Per-student prediction explanations
"""

import numpy as np
import pandas as pd
import shap
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import base64
from typing import Optional

FEATURE_DESCRIPTIONS = {
    "absences": "Number of school absences",
    "absence_level": "Absence severity",
    "failures": "Number of past class failures",
    "studytime": "Weekly study time",
    "study_efficiency": "Study efficiency score",
    "grade_trend": "Grade trend (G3 - G1)",
    "avg_grade": "Average grade across terms",
    "Medu": "Mother's education level",
    "Fedu": "Father's education level",
    "alcohol_index": "Alcohol consumption index",
    "goout": "Going out with friends",
    "freetime": "Free time after school",
    "health": "Current health status",
    "famrel": "Family relationship quality",
    "age": "Student age",
    "Walc": "Weekend alcohol consumption",
    "Dalc": "Workday alcohol consumption",
    "higher": "Wants higher education",
    "internet": "Internet access at home",
    "romantic": "In a romantic relationship",
}


class SHAPExplainer:
    def __init__(self, model, feature_cols: list):
        self.model = model
        self.feature_cols = feature_cols
        self.explainer = shap.TreeExplainer(model)

    def explain(self, X: pd.DataFrame) -> dict:
        """Generate SHAP explanation for a single student or batch."""
        shap_values = self.explainer.shap_values(X)
        expected_value = float(self.explainer.expected_value)

        # For binary classification, use class=1 (at-risk)
        if isinstance(shap_values, list):
            sv = shap_values[1]
        else:
            sv = shap_values

        results = []
        for i in range(len(X)):
            row_shap = sv[i] if len(X) > 1 else sv[0]
            feature_vals = X.iloc[i].to_dict()

            contributions = []
            for feat, shap_val in zip(self.feature_cols, row_shap):
                contributions.append({
                    "feature": feat,
                    "description": FEATURE_DESCRIPTIONS.get(feat, feat.replace("_", " ").title()),
                    "shap_value": round(float(shap_val), 4),
                    "feature_value": round(float(feature_vals.get(feat, 0)), 3),
                    "direction": "increases" if shap_val > 0 else "decreases",
                })

            contributions.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

            results.append({
                "expected_value": round(expected_value, 4),
                "contributions": contributions,
                "top_risk_factors": [c for c in contributions[:5] if c["shap_value"] > 0],
                "top_protective_factors": [c for c in contributions[:5] if c["shap_value"] < 0],
            })

        return results[0] if len(results) == 1 else results

    def generate_explanation_text(self, explanation: dict, risk_score: float) -> str:
        """Convert SHAP values to plain-English explanation for faculty."""
        risk_pct = int(risk_score * 100)
        risk_factors = explanation["top_risk_factors"][:3]
        protective = explanation["top_protective_factors"][:2]

        lines = [f"This student has a {risk_pct}% predicted failure risk."]

        if risk_factors:
            lines.append("\nMain risk factors:")
            for f in risk_factors:
                lines.append(f"  • {f['description']} (impact: +{abs(f['shap_value']):.2f})")

        if protective:
            lines.append("\nProtective factors:")
            for f in protective:
                lines.append(f"  • {f['description']} (impact: -{abs(f['shap_value']):.2f})")

        return "\n".join(lines)

    def plot_waterfall(self, explanation: dict, student_name: str = "Student") -> str:
        """Generate a waterfall chart as base64 PNG."""
        top_n = 8
        contributions = explanation["contributions"][:top_n]

        features = [c["description"] for c in contributions]
        values = [c["shap_value"] for c in contributions]
        colors = ["#E8593C" if v > 0 else "#3B8BD4" for v in values]

        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor("#0f0f0f")
        ax.set_facecolor("#0f0f0f")

        bars = ax.barh(features, values, color=colors, height=0.6, edgecolor="none")

        ax.set_xlabel("SHAP Value (impact on risk prediction)", color="#aaa", fontsize=10)
        ax.set_title(f"Risk Factors — {student_name}", color="#fff", fontsize=12, pad=12)
        ax.tick_params(colors="#ccc", labelsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#333")
        ax.spines["bottom"].set_color("#333")
        ax.axvline(0, color="#555", linewidth=0.8)

        for bar, val in zip(bars, values):
            xpos = val + (0.005 if val >= 0 else -0.005)
            ha = "left" if val >= 0 else "right"
            ax.text(xpos, bar.get_y() + bar.get_height() / 2,
                    f"{val:+.3f}", va="center", ha=ha, color="#fff", fontsize=8)

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, bbox_inches="tight", facecolor="#0f0f0f")
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")


def load_explainer(model_path: str = "data/model/model.pkl",
                   features_path: str = "data/model/feature_cols.pkl") -> SHAPExplainer:
    model = joblib.load(model_path)
    feature_cols = joblib.load(features_path)
    return SHAPExplainer(model, feature_cols)
