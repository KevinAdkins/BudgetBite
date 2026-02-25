from flask import Flask
from routes.recipe_routes import recipe_bp

app = Flask(__name__)

# Register the blueprint for recipe-related routes
app.register_blueprint(recipe_bp, url_prefix='/api')

if __name__ == '__main__':
    # Set debug=True for development to see live logs
    app.run(debug=True, port=5000)