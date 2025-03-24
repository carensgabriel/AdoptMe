import os
from flask import Blueprint, json, render_template, jsonify, request, url_for
from bson import ObjectId
from database import mongo
from middleware import *
from datetime import datetime
from werkzeug.utils import secure_filename

user_bp = Blueprint("user", __name__)

#* ==================== HOME ==================== #

@user_bp.route("/home")
def home():
    return render_template("home.html")

#* ==================== PROFILE ==================== #

@user_bp.route("/profile")
def user_profile():
    return render_template("user/user_profile.html")
    # return render_template("404.html")

#* ==================== SYARAT ADOPSI ==================== #

@user_bp.route("/syarat_adopsi", methods=["GET", "POST"])
@login_required
def syarat_adopsi():
    try:
        if request.method == "POST":
            data = request.get_json()

            if not data or not data.get("setuju"):
                return jsonify({"success": False, "message": "Anda harus menyetujui syarat adopsi sebelum melanjutkan."}), 400

            return jsonify({"success": True, "redirect": url_for("user.submit_adoption")})
        
        return render_template("user/adopt/syarat_adopsi.html")

    except Exception as e:
        print("error:", e)
        return jsonify({"success": False, "message": "Terjadi kesalahan server!"}), 500

#* ==================== SUBMIT FORM ADOPSI ==================== #

UPLOAD_FOLDER = "static/uploads/ktp"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route("/submit_adoption", methods=["POST"])
@login_required
def submit_adoption():
    try:
        user = get_current_user()

        # Ambil JSON dari form data
        json_data = request.form.get("data")
        if not json_data:
            return jsonify({"success": False, "message": "Data adopsi tidak ditemukan!"}), 400
        
        data = json.loads(json_data)

        # Ambil file KTP dalam bentuk Base64
        file_ktp = request.form.get("uploadKTP")  # Ambil string Base64

        if not file_ktp:
            return jsonify({"success": False, "message": "Harap unggah KTP dalam format Base64."}), 400

        new_adoption = {
            "adopter": {
                "name": data.get("namaAdopter", ""),
                "datebirth": data.get("tglLahir", ""),
                "phone": data.get("telpAdopter", ""),
                "email": data.get("emailAdopter", ""),
                "address": data.get("alamatAdopter", ""),
                "occupation": data.get("pekerjaanAdopter", ""),
                "residence": data.get("tempatTinggalLain", "") if data.get("tempatTinggal") == "Other" else data.get("tempatTinggal", ""),
                "reason": data.get("alasanAdopsi", ""),
                "ktp_file": file_ktp
            },
            "animal": {
                "name": data.get("namaHewan", ""),
                "breed": data.get("breedHewan", ""),
                "gender": data.get("jkHewan", "")
            },
            "emergency_contact": {
                "name": data.get("namaDarurat", ""),
                "phone": data.get("telpDarurat", "")
            },
            "status": "Pending",
            "submitted_at": datetime.now(),
            "user": {
                "name": user["name"],
                "email": user["email"]
            }
        }

        mongo.db.form_adoption.insert_one(new_adoption)
        return jsonify({"success": True, "message": "Formulir berhasil dikirim!"})

    except Exception as e:
        print(e)
        return jsonify({"success": False, "message": f"Terjadi kesalahan: {e}"}), 500
    

@user_bp.route("/get_adoption/<adoption_id>", methods=["GET"])
@login_required
def get_adoption(adoption_id):
    try:
        adoption = mongo.db.form_adoption.find_one({"_id": ObjectId(adoption_id)})

        if not adoption:
            return jsonify({"success": False, "message": "Data adopsi tidak ditemukan"}), 404

        # Kirim data Base64 ke frontend
        return jsonify({
            "success": True,
            "adoption": {
                "adopter": adoption["adopter"],
                "animal": adoption["animal"],
                "status": adoption["status"],
                "submitted_at": adoption["submitted_at"].strftime("%d-%m-%Y"),
            }
        })

    except Exception as e:
        return jsonify({"success": False, "message": f"Terjadi kesalahan: {e}"}), 500
    
#* ==================== INFORMASI ADOPSI ==================== #

@user_bp.route("/adoption_info", methods=["GET"])
@login_required
def adoption_info():
    try:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            user = get_current_user()

            if not user or not user.get("email"):
                return jsonify({"success": False, "message": "User tidak ditemukan"}), 401

            form_adopsi = list(mongo.db.form_adoption.find({"user.name": user["name"]}))
            list_adoptions = []
            for adoption in form_adopsi:
                animal_info = mongo.db.animals.find_one({"name": adoption["animal"]["name"]}) if "animal" in adoption else None
                list_adoptions.append({
                    "animal": {
                        "name": animal_info["name"] if animal_info else "Tidak tersedia",
                        "image": animal_info["image"] if animal_info and "image" in animal_info else "static/img/default-animal.jpg"
                    },
                    "submission_date": adoption["submitted_at"].strftime("%d-%m-%Y") if "submitted_at" in adoption else "Tidak tersedia",
                    "status": adoption.get("status", "Pending")
                })

            return jsonify({"success": True, "message": list_adoptions})
        
        return render_template("user/adopt/adoption_info.html")
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500