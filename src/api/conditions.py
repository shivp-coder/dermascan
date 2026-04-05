"""Conditions knowledge base API."""

from flask import Blueprint, jsonify

from src.models.conditions import get_condition, list_conditions

conditions_bp = Blueprint("conditions", __name__, url_prefix="/api/conditions")


@conditions_bp.get("")
def list_all():
    return jsonify({"conditions": list_conditions()})


@conditions_bp.get("/<key>")
def get_one(key: str):
    c = get_condition(key)
    if c is None:
        return jsonify({"error": "Condition not found"}), 404
    return jsonify({"condition": c})
