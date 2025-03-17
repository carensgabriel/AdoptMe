import os
from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from database import mongo
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.admin_routes import admin_bp
from routes.animal_routes import animal_bp

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Konfigurasi aplikasi
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback_secret_key")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "fallback_jwt_key")
app.config["JWT_TOKEN_LOCATION"] = ["headers"]

# Konfigurasi MongoDB
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI tidak ditemukan! Pastikan environment sudah diatur.")

app.config["MONGO_URI"] = MONGO_URI

# Inisialisasi MongoDB dan JWT
mongo.init_app(app)
jwt = JWTManager(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(animal_bp)

@app.route("/")
def index():
    return render_template("home.html")

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(port=3333, debug=debug_mode)