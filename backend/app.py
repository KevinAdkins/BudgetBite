from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import pull
from routes.meal_routes import meal_bp
from routes.pricing_routes import pricing_bp

load_dotenv()

app = Flask(__name__)

# Enable CORS for frontend access
CORS(app)

# Maintainer note:
# Keep DB initialization before blueprint registration so first request does not
# race table creation when running in a fresh environment.
pull.init_db()

# Register blueprints
app.register_blueprint(meal_bp, url_prefix='/api')
app.register_blueprint(pricing_bp, url_prefix='/api')

@app.route('/')
def home():
    return jsonify({
        "message": "BudgetBite API",
        "version": "1.0",
        "endpoints": {
            "GET /api/meals": "Get all meals",
            "GET /api/meals/<name>": "Get specific meal",
            "GET /api/meals/search?name=<name>": "Search for meal (DB + API)",
            "GET /api/meals/search-by-ingredient?ingredient=<ingredient>&full=true&first=true": "Search by ingredient and optionally return full details for first match",
            "POST /api/pricing/ingredients": "Estimate total ingredient cost with Kroger API",
            "POST /api/meals": "Add new meal",
            "PUT /api/meals/<name>": "Update meal",
            "PATCH /api/meals/<name>/instructions": "Update instructions only",
            "DELETE /api/meals/<name>": "Delete meal"
        }
    })

if __name__ == "__main__":
    app.run(debug=True, port=5001)