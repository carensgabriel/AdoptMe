from flask import Blueprint, redirect, render_template, jsonify, url_for, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from database import mongo

auth_bp = Blueprint("auth", __name__)

# ============================================================ #

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")  # Pastikan file ini ada

    # Cek apakah request memiliki Content-Type JSON
    if request.content_type != "application/json":
        return jsonify({"success": False, "message": "Content-Type harus application/json"}), 415

    # Ambil data dari request JSON
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Cari user di database
    user = mongo.db.users.find_one({"username": username})

    # Jika user tidak ditemukan
    if not user:
        return jsonify({"success": False, "message": "User tidak ditemukan!"}), 401

    # Cek password hash
    if "password" not in user or not check_password_hash(user["password"], password):
        return jsonify({"success": False, "message": "Username atau password salah."}), 401

    # Simpan user ke dalam session
    session["user_id"] = str(user["_id"])
    session["role"] = user["role"]
    session.modified = True  # Pastikan session diperbarui

    # Cek role dan arahkan ke halaman yang sesuai
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
