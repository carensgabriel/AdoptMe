from flask import Flask, render_template
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.admin_routes import admin_bp
from routes.animal_routes import animal_bp
from database import mongo
from dotenv import load_dotenv
from datetime import timedelta
import os

load_dotenv()
app = Flask(__name__)
MONGO_URI = os.getenv("MONGO_URI")
app.config["MONGO_URI"] = MONGO_URI
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback_secret_key")
app.permanent_session_lifetime = timedelta(minutes=30)  # timeout = 30 menit

mongo.init_app(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(animal_bp)

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "True"
    app.run(port=3333, debug=debug_mode)