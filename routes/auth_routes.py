import re
from flask import Blueprint, redirect, render_template, jsonify, url_for, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from database import mongo

auth_bp = Blueprint("auth", __name__)

# ============================================================ #

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", title="Login")

    if request.content_type != "application/json":
        return jsonify({"success": False, "message": "Content-Type harus application/json"}), 415

    data = request.get_json()
    identifier = data.get("identifier")  # Bisa username atau email
    password = data.get("password")

    # Cari user berdasarkan username atau email
    user = mongo.db.users.find_one({"$or": [{"username": identifier}, {"email": identifier}]})

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"success": False, "message": "Username/email atau password salah."}), 400

    session.permanent = True
    session["user_id"] = str(user["_id"])
    session["username"] = user["username"]
    session["email"] = user["email"]
    session["role"] = user["role"]
    session.modified = True

    redirect_url = url_for("admin.dashboard") if user["role"] == "admin" else url_for("user.home")
    
    return jsonify({"success": True, "redirect": redirect_url})

# ============================================================ #

@auth_bp.route("/logout")
def logout():
    session.clear()
    session.modified = True
    return redirect(url_for("auth.login"))

# ============================================================ #

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", title="Register")

    # Jika metode POST
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # Validasi input
    if not username or not email or not password:
        return jsonify({"success": False, "message": "Username, email, dan password wajib diisi!"}), 400

    # Cek format email
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(email_regex, email):
        return jsonify({"success": False, "message": "Format email tidak valid!"}), 400

    # Cek apakah username atau email sudah terdaftar
    existing_user = mongo.db.users.find_one({"$or": [{"username": username}, {"email": email}]})
    if existing_user:
        if existing_user["username"] == username:
            return jsonify({"success": False, "message": "Username sudah digunakan!"}), 400
        if existing_user["email"] == email:
            return jsonify({"success": False, "message": "Email sudah digunakan!"}), 400

    # Hash password sebelum menyimpan ke database
    hashed_password = generate_password_hash(password)

    mongo.db.users.insert_one({
        "username": username,
        "email": email,
        "password": hashed_password,
        "role": "user"
    })

    return jsonify({"success": True, "message": "Registrasi berhasil!"}), 201