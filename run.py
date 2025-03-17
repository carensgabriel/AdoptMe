from flask import Flask, render_template
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.admin_routes import admin_bp
from routes.animal_routes import animal_bp
from database import mongo
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"
app.config["MONGO_URI"] = "mongodb+srv://carens:uMR6GKMHifGFACmL@AdoptMe.vngse.mongodb.net/adopsi"
app.config["JWT_SECRET_KEY"] = "supersecretkey"  # Ganti dengan kunci rahasia yang kuat
app.config["JWT_TOKEN_LOCATION"] = ["headers"]  # Tentukan lokasi JWT (misalnya di header)

# Inisialisasi JWTManager
jwt = JWTManager(app)

mongo.init_app(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(animal_bp)

@app.route("/")
def index():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(port=3333, debug=True)