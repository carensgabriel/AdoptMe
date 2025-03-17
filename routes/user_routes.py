from datetime import datetime
from bson import ObjectId
from flask import Blueprint, render_template, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import mongo
from middleware import login_required

user_bp = Blueprint("user", __name__)

#* ==================== HOME ==================== #

@user_bp.route("/home")
def home():
    return render_template("home.html")  # Halaman home untuk user

#* ==================== USER PROFILE ==================== #

def get_user_data(user_id):
    try:
        # Ambil data pengguna dari database berdasarkan user_id
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            # Mengubah ObjectId menjadi string agar bisa diproses
            user['_id'] = str(user['_id'])
            return user
        else:
            return None  # Jika pengguna tidak ditemukan
    except Exception as e:
        print(f"Error fetching user data: {e}")
        return None

@user_bp.route("/profile")
@jwt_required()
def user_profile():
    try:
        # Mendapatkan identitas pengguna dari JWT
        current_user = get_jwt_identity()

        # Ambil data pengguna dari database menggunakan current_user (ID atau email yang ada di JWT)
        user = get_user_data(current_user)

        # Jika pengguna tidak ditemukan, tampilkan error
        if user is None:
            return jsonify(message="User not found"), 404

        # Render halaman profil pengguna dengan data pengguna
        return render_template("user/user_profile.html", user=user)

    except Exception as e:
        return jsonify(message=f"An error occurred: {str(e)}"), 500

#* ==================== SUBMIT ADOPTION ==================== #

@user_bp.route("/submit_adoption", methods=["POST"])
def submit_adoption():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "message": "Data tidak valid!"}), 400

        new_adoption = {
            "adopter": {
                "name": data["namaAdopter"],
                "age": data["umurAdopter"],
                "phone": data["telpAdopter"],
                "email": data["emailAdopter"],
                "job": data["pekerjaanAdopter"],
                "residence": data["tempatTinggal"]
            },
            "animal": {
                "name": data["namaHewan"],
                "species": data["breedHewan"],  # Ganti spesiesHewan dengan breedHewan
                "gender": data["jenisKelamin"]
            },
            "status": "Pending",
            "submitted_at": datetime.now()
        }

        mongo.db.form_adoption.insert_one(new_adoption)
        return jsonify({"success": True, "message": "Formulir berhasil dikirim!"})

    except KeyError as ke:
        print("DEBUG: KeyError:", str(ke))  # Debugging
        return jsonify({"success": False, "message": f"Field {str(ke)} tidak ditemukan dalam request!"}), 400

    except Exception as e:
        print("DEBUG: Error:", str(e))  # Debugging
        return jsonify({"success": False, "message": f"Terjadi kesalahan: {str(e)}"}), 500