"""Tests for the triage engine."""

import pytest

from src.engine.triage import analyze, _assess_abcde, _build_next_steps
from src.models.analysis import TriageResult


def _make_features(
    symmetry_score=0.9,
    border_regularity="regular",
    lesion_area_ratio=0.1,
    color_variance="low",
    is_dark=False,
    is_red_dominant=False,
    is_brown=False,
    texture_type="smooth",
    mean_r=150.0,
    mean_g=120.0,
    mean_b=100.0,
):
    """Helper to build a features dict for testing."""
    return {
        "dimensions": {"width": 200, "height": 200},
        "color": {
            "mean_rgb": {"r": mean_r, "g": mean_g, "b": mean_b},
            "std_rgb": {"r": 20.0, "g": 20.0, "b": 20.0},
            "is_dark": is_dark,
            "is_red_dominant": is_red_dominant,
            "is_brown": is_brown,
            "color_variance": color_variance,
        },
        "shape": {
            "lesion_area_ratio": lesion_area_ratio,
            "symmetry_score": symmetry_score,
            "border_regularity": border_regularity,
        },
        "texture": {
            "mean_local_variance": 200.0,
            "texture_type": texture_type,
        },
    }


class TestAnalyze:
    def test_returns_triage_result(self):
        features = _make_features()
        result = analyze(features)
        assert isinstance(result, TriageResult)

    def test_returns_top_3_conditions(self):
        features = _make_features()
        result = analyze(features)
        assert len(result.top_conditions) == 3

    def test_severity_in_valid_range(self):
        features = _make_features()
        result = analyze(features)
        assert 1 <= result.severity_score <= 5

    def test_severity_label_present(self):
        features = _make_features()
        result = analyze(features)
        assert result.severity_label in [
            "Very Mild", "Mild", "Moderate", "Significant", "Urgent",
        ]

    def test_next_steps_not_empty(self):
        features = _make_features()
        result = analyze(features)
        assert len(result.next_steps) > 0

    def test_disclaimer_present(self):
        features = _make_features()
        result = analyze(features)
        assert "not" in result.disclaimer.lower()
        assert "diagnosis" in result.disclaimer.lower()

    def test_high_risk_features_increase_severity(self):
        # Asymmetric, irregular border, multi-color, large, dark
        low_risk = _make_features()
        high_risk = _make_features(
            symmetry_score=0.4,
            border_regularity="irregular",
            color_variance="high",
            lesion_area_ratio=0.5,
            is_dark=True,
        )
        low_result = analyze(low_risk)
        high_result = analyze(high_risk)
        assert high_result.severity_score >= low_result.severity_score

    def test_concerning_abcde_triggers_urgent_steps(self):
        features = _make_features(
            symmetry_score=0.3,
            border_regularity="irregular",
            color_variance="high",
        )
        result = analyze(features)
        steps_text = " ".join(result.next_steps).lower()
        assert "professional" in steps_text

    def test_to_dict_structure(self):
        features = _make_features()
        result = analyze(features)
        d = result.to_dict()
        assert "top_conditions" in d
        assert "severity_score" in d
        assert "severity_label" in d
        assert "next_steps" in d
        assert "doctor_recommendation" in d
        assert "abcde_assessment" in d
        assert "disclaimer" in d

    def test_condition_confidence_not_over_85(self):
        features = _make_features()
        result = analyze(features)
        for cond in result.top_conditions:
            assert cond.confidence_percent <= 85.0


class TestABCDE:
    def test_normal_symmetry(self):
        features = _make_features(symmetry_score=0.9)
        abcde = _assess_abcde(features)
        assert abcde["asymmetry"] == "normal"

    def test_concerning_symmetry(self):
        features = _make_features(symmetry_score=0.4)
        abcde = _assess_abcde(features)
        assert abcde["asymmetry"] == "concerning"

    def test_normal_border(self):
        features = _make_features(border_regularity="regular")
        abcde = _assess_abcde(features)
        assert abcde["border"] == "normal"

    def test_concerning_border(self):
        features = _make_features(border_regularity="irregular")
        abcde = _assess_abcde(features)
        assert abcde["border"] == "concerning"

    def test_evolution_not_assessable(self):
        features = _make_features()
        abcde = _assess_abcde(features)
        assert "unable" in abcde["evolution"]


class TestBuildNextSteps:
    def test_urgent_severity_mentions_dermatologist(self):
        abcde = {"asymmetry": "normal", "border": "normal",
                 "color": "normal", "diameter": "normal",
                 "evolution": "unable_to_assess"}
        steps = _build_next_steps(5, abcde)
        steps_text = " ".join(steps).lower()
        assert "dermatologist" in steps_text or "healthcare" in steps_text

    def test_low_severity_mentions_monitor(self):
        abcde = {"asymmetry": "normal", "border": "normal",
                 "color": "normal", "diameter": "normal",
                 "evolution": "unable_to_assess"}
        steps = _build_next_steps(1, abcde)
        steps_text = " ".join(steps).lower()
        assert "monitor" in steps_text

    def test_always_includes_disclaimer_step(self):
        abcde = {"asymmetry": "normal", "border": "normal",
                 "color": "normal", "diameter": "normal",
                 "evolution": "unable_to_assess"}
        for severity in range(1, 6):
            steps = _build_next_steps(severity, abcde)
            last_step = steps[-1].lower()
            assert "not a diagnosis" in last_step
