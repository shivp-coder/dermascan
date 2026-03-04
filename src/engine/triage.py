"""Core triage engine for dermatological image analysis.

Uses image feature extraction and rule-based scoring to produce
a structured triage result with condition matches, severity score,
and recommendations.

IMPORTANT: This is NOT a diagnostic tool. Results are for informational
triage purposes only and must always recommend professional consultation.
"""

from src.models.analysis import (
    SEVERITY_LABELS,
    SEVERITY_RECOMMENDATIONS,
    ConditionMatch,
    TriageResult,
)
from src.models.conditions import CONDITIONS_DB


def analyze(features: dict) -> TriageResult:
    """Perform triage analysis on extracted image features.

    Args:
        features: Dictionary of extracted image features from
                  image_processing.extract_features().

    Returns:
        TriageResult with top conditions, severity, and recommendations.
    """
    abcde = _assess_abcde(features)
    scores = _score_conditions(features, abcde)

    # Sort by score descending and take top 3
    sorted_conditions = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_3 = sorted_conditions[:3]

    # Normalize confidence percentages for top 3
    total_score = sum(s for _, s in top_3)
    if total_score == 0:
        total_score = 1

    top_conditions = []
    for cond_key, score in top_3:
        condition = CONDITIONS_DB[cond_key]
        confidence = (score / total_score) * 100
        # Cap individual confidence and ensure minimum for top matches
        confidence = min(confidence, 85.0)
        top_conditions.append(
            ConditionMatch(
                condition_name=condition.name,
                confidence_percent=confidence,
                description=condition.description,
            )
        )

    # Determine severity from highest-severity matched condition
    severity = _determine_severity(top_conditions, abcde)
    severity_label = SEVERITY_LABELS.get(severity, "Unknown")

    # Build next steps
    next_steps = _build_next_steps(severity, abcde)

    return TriageResult(
        top_conditions=top_conditions,
        severity_score=severity,
        severity_label=severity_label,
        next_steps=next_steps,
        doctor_recommendation=SEVERITY_RECOMMENDATIONS.get(severity, ""),
        abcde_assessment=abcde,
    )


def _assess_abcde(features: dict) -> dict:
    """Apply ABCDE rule assessment for pigmented lesions.

    A = Asymmetry
    B = Border irregularity
    C = Color variation
    D = Diameter (estimated)
    E = Evolution (cannot determine from single image)
    """
    shape = features.get("shape", {})
    color = features.get("color", {})

    symmetry_score = shape.get("symmetry_score", 0.5)
    asymmetry = "concerning" if symmetry_score < 0.65 else (
        "mild" if symmetry_score < 0.8 else "normal"
    )

    border_reg = shape.get("border_regularity", "regular")
    border = "concerning" if border_reg == "irregular" else (
        "mild" if border_reg == "somewhat_irregular" else "normal"
    )

    color_var = color.get("color_variance", "low")
    color_assessment = "concerning" if color_var == "high" else (
        "mild" if color_var == "moderate" else "normal"
    )

    # Diameter estimation from lesion area ratio
    area_ratio = shape.get("lesion_area_ratio", 0)
    diameter = "concerning" if area_ratio > 0.3 else (
        "mild" if area_ratio > 0.15 else "normal"
    )

    return {
        "asymmetry": asymmetry,
        "border": border,
        "color": color_assessment,
        "diameter": diameter,
        "evolution": "unable_to_assess_from_single_image",
    }


def _score_conditions(features: dict, abcde: dict) -> dict[str, float]:
    """Score each condition based on features and ABCDE assessment."""
    scores = {}
    color = features.get("color", {})
    shape = features.get("shape", {})
    texture = features.get("texture", {})

    for key, condition in CONDITIONS_DB.items():
        score = 0.0
        morph = condition.morphology

        # Symmetry scoring
        if morph.get("symmetry") == "asymmetric":
            if abcde["asymmetry"] == "concerning":
                score += 3.0
            elif abcde["asymmetry"] == "mild":
                score += 1.5
        elif morph.get("symmetry") == "symmetric":
            if abcde["asymmetry"] == "normal":
                score += 2.0

        # Border scoring
        if morph.get("border") == "irregular":
            if abcde["border"] == "concerning":
                score += 2.5
            elif abcde["border"] == "mild":
                score += 1.0
        elif morph.get("border") in ("well_defined", "rolled"):
            if abcde["border"] == "normal":
                score += 1.5

        # Color scoring
        if morph.get("color_uniformity") == "multi_color":
            if abcde["color"] == "concerning":
                score += 3.0
            elif abcde["color"] == "mild":
                score += 1.0
        elif morph.get("color_uniformity") == "uniform":
            if abcde["color"] == "normal":
                score += 1.5

        # Color-specific matching
        if color.get("is_dark") and "black" in morph.get("typical_colors", []):
            score += 2.0
        if color.get("is_red_dominant") and "red" in morph.get("typical_colors", []):
            score += 1.5
        if color.get("is_brown") and "brown" in morph.get("typical_colors", []):
            score += 1.5

        # Surface/texture scoring
        texture_type = texture.get("texture_type", "smooth")
        surface = morph.get("surface", "smooth")
        if surface == "scaly" and texture_type == "rough":
            score += 2.0
        elif surface == "smooth" and texture_type == "smooth":
            score += 1.5
        elif surface == "rough" and texture_type in ("rough", "moderate"):
            score += 1.5

        # Size scoring
        if morph.get("symmetry") == "asymmetric" and abcde["diameter"] == "concerning":
            score += 1.5

        scores[key] = score

    return scores


def _determine_severity(
    top_conditions: list[ConditionMatch], abcde: dict
) -> int:
    """Determine overall severity score."""
    # Start with the typical severity of the top condition
    if not top_conditions:
        return 1

    top_name = top_conditions[0].condition_name
    severity = 1
    for condition in CONDITIONS_DB.values():
        if condition.name == top_name:
            severity = condition.typical_severity
            break

    # ABCDE risk escalation — if multiple concerning factors, escalate
    concerning_count = sum(
        1 for v in abcde.values()
        if v == "concerning"
    )
    if concerning_count >= 3:
        severity = max(severity, 4)
    elif concerning_count >= 2:
        severity = max(severity, 3)

    # Always cap at 5
    return min(severity, 5)


def _build_next_steps(severity: int, abcde: dict) -> list[str]:
    """Build actionable next steps based on severity and assessment."""
    steps = []

    if severity >= 4:
        steps.append(
            "Seek prompt evaluation by a dermatologist or healthcare "
            "professional."
        )
        steps.append(
            "Do not attempt to treat or remove the lesion yourself."
        )
        steps.append(
            "Take additional photos from different angles for your "
            "doctor visit."
        )
    elif severity == 3:
        steps.append(
            "Schedule an appointment with a healthcare professional "
            "within 2-4 weeks."
        )
        steps.append(
            "Monitor the area for any changes in size, shape, or color."
        )
    elif severity == 2:
        steps.append(
            "Consider over-the-counter treatments appropriate for the "
            "suspected condition."
        )
        steps.append(
            "If symptoms persist beyond 2 weeks, consult a healthcare "
            "professional."
        )
    else:
        steps.append("Monitor the area for any changes over time.")
        steps.append(
            "Consult a healthcare professional if you notice any "
            "changes or have concerns."
        )

    # ABCDE-specific guidance
    if abcde.get("asymmetry") == "concerning":
        steps.append(
            "The asymmetric appearance warrants professional evaluation."
        )
    if abcde.get("border") == "concerning":
        steps.append(
            "Irregular borders were noted — discuss this with your doctor."
        )
    if abcde.get("color") == "concerning":
        steps.append(
            "Multiple colors were detected — this should be evaluated "
            "by a professional."
        )

    steps.append(
        "Remember: this analysis is not a diagnosis. Always consult a "
        "qualified healthcare professional."
    )

    return steps
