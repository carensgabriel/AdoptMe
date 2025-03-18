from datetime import timedelta
from flask import Blueprint, redirect, render_template, jsonify, url_for, request, session
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash
from database import mongo

auth_bp = Blueprint("auth", __name__)

# ============================================================ #

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.content_type != "application/json":
        return jsonify({"success": False, "message": "Content-Type harus application/json"}), 415

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = mongo.db.users.find_one({"username": username})

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"success": False, "message": "Username atau password salah."}), 401

    session["user_id"] = str(user["_id"])
    session["role"] = user["role"]
    session.modified = True 

    redirect_url = url_for("admin.dashboard") if user["role"] == "admin" else url_for("user.home")
    
    return jsonify({"success": True, "redirect": redirect_url})

# ============================================================ #

@auth_bp.route("/logout")
def logout():
    session.clear()
    session.modified = True
    return redirect(url_for("index"))

# ============================================================ #

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    # Jika metode POST
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "message": "Username dan password wajib diisi!"}), 400

    user = mongo.db.users.find_one({"username": username})

    if user:
        return jsonify({"success": False, "message": "Username sudah digunakan!"}), 400

    hashed_password = generate_password_hash(password)
    mongo.db.users.insert_one({
        "username": username, 
        "password": hashed_password,
        "role": "user"
    })

    return jsonify({"success": True, "message": "Registrasi berhasil!"}), 201
