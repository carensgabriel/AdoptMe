from flask import Blueprint, render_template, jsonify, request
from bson import ObjectId
from database import mongo
from middleware import login_required
from datetime import datetime

user_bp = Blueprint("user", __name__)

#* ==================== HOME ==================== #

@user_bp.route("/home")
def home():
    return render_template("home.html")

#* ==================== PROFILE ==================== #

@user_bp.route("/profile")
def user_profile():
    return render_template("user/user_profile.html")

@user_bp.route("/404")
def under_development():
    return render_template("404.html")

#* ==================== SUBMIT ADOPTION ==================== #

@user_bp.route("/submit_adoption", methods=["POST"])
@login_required
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