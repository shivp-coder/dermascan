"""Data models for triage analysis results."""

from dataclasses import dataclass, field


@dataclass
class ConditionMatch:
    condition_name: str
    confidence_percent: float
    description: str

    def to_dict(self) -> dict:
        return {
            "condition": self.condition_name,
            "confidence_percent": round(self.confidence_percent, 1),
            "description": self.description,
        }


@dataclass
class TriageResult:
    top_conditions: list[ConditionMatch] = field(default_factory=list)
    severity_score: int = 1
    severity_label: str = "Very Mild"
    next_steps: list[str] = field(default_factory=list)
    doctor_recommendation: str = ""
    abcde_assessment: dict = field(default_factory=dict)
    disclaimer: str = (
        "This analysis is for informational purposes only and does not "
        "constitute a medical diagnosis. Please consult a qualified "
        "healthcare professional for proper evaluation and treatment."
    )

    def to_dict(self) -> dict:
        return {
            "top_conditions": [c.to_dict() for c in self.top_conditions],
            "severity_score": self.severity_score,
            "severity_label": self.severity_label,
            "next_steps": self.next_steps,
            "doctor_recommendation": self.doctor_recommendation,
            "abcde_assessment": self.abcde_assessment,
            "disclaimer": self.disclaimer,
        }


SEVERITY_LABELS = {
    1: "Very Mild",
    2: "Mild",
    3: "Moderate",
    4: "Significant",
    5: "Urgent",
}

SEVERITY_RECOMMENDATIONS = {
    1: (
        "This appears to be a cosmetic or self-resolving concern. "
        "Monitor for any changes and consult a healthcare professional "
        "if the condition changes or persists."
    ),
    2: (
        "This may respond to over-the-counter treatments. If symptoms "
        "persist or worsen after 2 weeks of treatment, please consult "
        "a healthcare professional."
    ),
    3: (
        "It is recommended to see a healthcare professional within "
        "2-4 weeks for proper evaluation and treatment."
    ),
    4: (
        "Please schedule an appointment with a dermatologist within "
        "1 week. This warrants professional medical evaluation."
    ),
    5: (
        "URGENT: Please see a dermatologist or healthcare professional "
        "within 24-48 hours. If not possible, visit an urgent care "
        "facility for evaluation."
    ),
}
