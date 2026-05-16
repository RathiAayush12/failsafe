"""
FailSafe — Intervention Plan Generator
Rule-based + template system for generating personalized interventions
"""

from typing import List, Dict


INTERVENTION_RULES = [
    {
        "condition": lambda s, e: s["absences"] > 15,
        "category": "Attendance",
        "priority": "High",
        "action": "Schedule immediate meeting with student and guardian to discuss attendance pattern.",
        "followup": "Weekly check-in with class teacher for 4 weeks."
    },
    {
        "condition": lambda s, e: s["absences"] > 5,
        "category": "Attendance",
        "priority": "Medium",
        "action": "Send attendance warning letter to guardian. Log absences for 2 weeks.",
        "followup": "Review attendance after 2 weeks."
    },
    {
        "condition": lambda s, e: s.get("failures", 0) >= 2,
        "category": "Academic Support",
        "priority": "High",
        "action": "Enroll student in remedial classes immediately. Assign academic mentor.",
        "followup": "Monthly progress review with subject teachers."
    },
    {
        "condition": lambda s, e: s.get("failures", 0) == 1,
        "category": "Academic Support",
        "priority": "Medium",
        "action": "Offer extra tutoring sessions. Review study habits with student.",
        "followup": "Bi-weekly assignment check."
    },
    {
        "condition": lambda s, e: s.get("studytime", 0) <= 1,
        "category": "Study Habits",
        "priority": "Medium",
        "action": "Connect student with study skills counsellor. Share structured study plan.",
        "followup": "Review progress after 3 weeks."
    },
    {
        "condition": lambda s, e: s.get("alcohol_index", 0) > 2.5,
        "category": "Wellbeing",
        "priority": "High",
        "action": "Refer student to school counsellor. Engage guardian confidentially.",
        "followup": "Counsellor to provide bi-weekly updates."
    },
    {
        "condition": lambda s, e: s.get("health", 5) <= 2,
        "category": "Wellbeing",
        "priority": "Medium",
        "action": "Refer to school nurse. Consider flexible assessment deadlines.",
        "followup": "Check health status after 2 weeks."
    },
    {
        "condition": lambda s, e: s.get("famrel", 5) <= 2,
        "category": "Family Support",
        "priority": "Medium",
        "action": "Schedule parent-teacher meeting. Engage school social worker if needed.",
        "followup": "Follow up after parent meeting."
    },
    {
        "condition": lambda s, e: s.get("internet", 1) == 0,
        "category": "Resources",
        "priority": "Low",
        "action": "Provide access to school computer lab during free periods.",
        "followup": "Confirm access within 1 week."
    },
    {
        "condition": lambda s, e: s.get("higher", 1) == 0,
        "category": "Motivation",
        "priority": "Medium",
        "action": "Career counselling session to explore goals and motivations.",
        "followup": "Follow-up meeting in 1 month."
    },
    {
        "condition": lambda s, e: any(
            c["feature"] in ["avg_grade", "grade_trend"] and c["shap_value"] > 0.1
            for c in e.get("top_risk_factors", [])
        ),
        "category": "Academic Support",
        "priority": "High",
        "action": "Review all subject grades. Identify weakest subjects and assign targeted support.",
        "followup": "Mid-term grade check."
    },
]


def generate_intervention_plan(
    student_data: Dict,
    explanation: Dict,
    risk_score: float,
    student_name: str = "Student"
) -> Dict:
    """
    Generate a personalized intervention plan based on student data and SHAP explanation.
    """
    interventions = []

    for rule in INTERVENTION_RULES:
        try:
            if rule["condition"](student_data, explanation):
                interventions.append({
                    "category": rule["category"],
                    "priority": rule["priority"],
                    "action": rule["action"],
                    "followup": rule["followup"],
                })
        except Exception:
            continue

    # Deduplicate by category (keep highest priority)
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    seen_categories = {}
    for item in sorted(interventions, key=lambda x: priority_order[x["priority"]]):
        if item["category"] not in seen_categories:
            seen_categories[item["category"]] = item

    interventions = list(seen_categories.values())
    interventions.sort(key=lambda x: priority_order[x["priority"]])

    # If no rules triggered but risk is high
    if not interventions and risk_score >= 0.5:
        interventions.append({
            "category": "General Support",
            "priority": "Medium",
            "action": "Schedule a one-on-one meeting with the student to understand challenges.",
            "followup": "Review after 2 weeks."
        })

    risk_level = (
        "High" if risk_score >= 0.7
        else "Medium" if risk_score >= 0.4
        else "Low"
    )

    summary = _generate_summary(student_name, risk_score, risk_level, interventions)

    return {
        "student_name": student_name,
        "risk_score": round(risk_score, 3),
        "risk_level": risk_level,
        "summary": summary,
        "interventions": interventions,
        "total_actions": len(interventions),
    }


def _generate_summary(name: str, score: float, level: str, interventions: List[Dict]) -> str:
    high = [i for i in interventions if i["priority"] == "High"]
    medium = [i for i in interventions if i["priority"] == "Medium"]

    lines = [
        f"{name} is flagged as {level} risk with a predicted failure probability of {int(score*100)}%."
    ]
    if high:
        cats = ", ".join(i["category"] for i in high)
        lines.append(f"Immediate action required in: {cats}.")
    if medium:
        cats = ", ".join(i["category"] for i in medium)
        lines.append(f"Medium-priority areas: {cats}.")
    if not interventions:
        lines.append("No specific interventions triggered. Monitor student progress closely.")

    return " ".join(lines)
