from routes import *
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_pymongo import PyMongo
from werkzeug.security import check_password_hash
from database import mongo
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"
app.config["MONGO_URI"] = "mongodb://localhost:27017/adopsi"
mongo.init_app(app)

mongo = PyMongo(app)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")  # Pastikan ada file login.html

    elif request.method == "POST":
        data = request.json
        username = data.get("username")
        password = data.get("password")

        user = mongo.db.users.find_one({"username": username})

        if user and check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            session["role"] = user["role"]  # Simpan role (admin/user)
            return jsonify({"success": True, "redirect_url": url_for("home")})

        return jsonify({"success": False, "message": "Username atau password salah."})

@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("home.html")  # Pastikan ada file home.html

if __name__ == "__main__":
    app.run(debug=True, port=3333)