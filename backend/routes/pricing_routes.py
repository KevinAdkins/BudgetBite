from flask import Blueprint, jsonify, request

import kroger_pricing


pricing_bp = Blueprint("pricing_bp", __name__)


@pricing_bp.route("/pricing/ingredients", methods=["POST"])
def price_ingredients():
    """Get estimated ingredient total using Kroger API by zip code."""
    data = request.get_json(silent=True) or {}
    ingredients = data.get("ingredients") or []
    zip_code = (data.get("zipCode") or "").strip()
    price_strategy = (data.get("priceStrategy") or "average_top3").strip()

    if not isinstance(ingredients, list) or not ingredients:
        return jsonify({"error": "ingredients must be a non-empty list"}), 400
    if not zip_code:
        return jsonify({"error": "zipCode is required"}), 400

    normalized = [str(i).strip() for i in ingredients if str(i).strip()]
    if not normalized:
        return jsonify({"error": "ingredients must contain at least one non-empty value"}), 400

    try:
        result = kroger_pricing.estimate_ingredient_total(
            normalized,
            zip_code,
            price_strategy=price_strategy,
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to estimate ingredient pricing: {str(e)}"}), 502