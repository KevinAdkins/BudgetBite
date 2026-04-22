from flask import Blueprint, jsonify, request
import kroger_pricing
from models import database


pricing_bp = Blueprint("pricing_bp", __name__)


@pricing_bp.route("/pricing/ingredients", methods=["POST"])
def price_ingredients():
    """Get estimated ingredient total using Kroger API by zip code."""
    data = request.get_json(silent=True) or {}
    ingredients = data.get("ingredients") or []
    zip_code = (data.get("zipCode") or "").strip()
    requested_strategy = (data.get("priceStrategy") or "average_top3").strip()
    price_strategy = kroger_pricing.normalize_price_strategy(requested_strategy)
    persist = bool(data.get("persist", False))
    meal_id = (data.get("mealId") or "").strip() or None
    source = (data.get("source") or "api").strip() or "api"

    if not isinstance(ingredients, list) or not ingredients:
        return jsonify({"error": "ingredients must be a non-empty list"}), 400
    if not zip_code:
        return jsonify({"error": "zipCode is required"}), 400
    if requested_strategy and requested_strategy.lower() not in kroger_pricing.ALLOWED_PRICE_STRATEGIES:
        return jsonify(
            {
                "error": "Invalid priceStrategy",
                "allowed": list(kroger_pricing.ALLOWED_PRICE_STRATEGIES),
            }
        ), 400

    normalized = [str(i).strip() for i in ingredients if str(i).strip()]
    if not normalized:
        return jsonify({"error": "ingredients must contain at least one non-empty value"}), 400

    try:
        result = kroger_pricing.estimate_ingredient_total(
            normalized,
            zip_code,
            price_strategy=price_strategy,
        )

        if persist:
            run_id = database.save_pricing_run(result, meal_id=meal_id, source=source)
            result["runId"] = run_id
            result["persisted"] = True
        else:
            result["persisted"] = False

        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to estimate ingredient pricing: {str(e)}"}), 502