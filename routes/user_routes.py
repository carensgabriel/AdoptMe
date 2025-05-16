import base64
import os
from flask import Blueprint, json, render_template, jsonify, request, url_for
from bson import ObjectId
from database import mongo
from middleware import *
from datetime import datetime
from werkzeug.utils import secure_filename

user_bp = Blueprint("user", __name__)

bulan_indonesia = {
    "January": "Januari", "February": "Februari", "March": "Maret",
    "April": "April", "May": "Mei", "June": "Juni",
    "July": "Juli", "August": "Agustus", "September": "September",
    "October": "Oktober", "November": "November", "December": "Desember"
}

# def formatDate(tanggal):
#     """
#     Mengubah format datetime ke format 'DD Bulan YYYY' dalam bahasa Indonesia.
    
#     Args:
#         tanggal (datetime): Objek datetime yang akan diformat.
    
#     Returns:
#         str: Tanggal dalam format 'DD Bulan YYYY'
#     """
#     if not tanggal:
#         return "Tidak tersedia"

#     tanggal_formatted = tanggal.strftime("%d %B %Y")  # Contoh: "21 March 2024"
    
#     # Ganti nama bulan Inggris dengan bahasa Indonesia
#     for en, id in bulan_indonesia.items():
#         tanggal_formatted = tanggal_formatted.replace(en, id)

#     return tanggal_formatted

#* ==================== HOME ==================== #

@user_bp.route("/")
def home():
    return render_template("home.html", title="Home")

@user_bp.route("/article")
def article():
    return render_template("article.html", title="Artikel")

@user_bp.route("/404")
def under_dev():
    return render_template("404.html", title="404")

#* ==================== PROFILE ==================== #

@user_bp.route("/profile")
def user_profile():
    username = session.get('username', 'User')
    return render_template("user/user_profile.html", title="Profile", auth={'username': username})

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
        
        return render_template("user/adopt/syarat_adopsi.html", title="Syarat Adopsi")

    except Exception as e:
        print("error:", e)
        return jsonify({"success": False, "message": "Terjadi kesalahan server!"}), 500

#* ==================== SUBMIT FORM ADOPSI ==================== #

@user_bp.route("/submit_adoption", methods=["POST"])
@login_required
def submit_adoption():
    try:
        user = get_current_user()
        json_data = request.form.get("data")

        if not json_data:
            return jsonify({"success": False, "message": "Data adopsi tidak ditemukan!"}), 400
        
        data = json.loads(json_data)
        file_ktp = request.form.get("uploadKTP")

        if not file_ktp:
            return jsonify({"success": False, "message": "Harap unggah KTP dalam format Base64."}), 400

        new_adoption = {
            "adopter": {
                "name": data.get("namaAdopter", ""),
                "datebirth": datetime.strptime(data.get("tglLahir", ""), "%Y-%m-%d"),
                "phone": data.get("telpAdopter", ""),
                "email": data.get("emailAdopter", ""),
                "address": data.get("alamatAdopter", ""),
                "occupation": data.get("pekerjaanLain", "") if data.get("pekerjaanAdopter") == "Other" else data.get("pekerjaanAdopter", ""),
                "residence": data.get("tempatTinggalLain", "") if data.get("tempatTinggal") == "Other" else data.get("tempatTinggal", ""),
                "reason": data.get("alasanAdopsi", ""),
                "ktp_file": file_ktp
            },
            "animal_id": ObjectId(data.get("idHewan", "")),
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
            "submission_date": datetime.now(),
            "visit_date": "",
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
                    "_id": str(adoption["_id"]),
                    "animal": {
                        "name": animal_info["name"] if animal_info else "Tidak tersedia",
                        "image": animal_info["image"] if animal_info and "image" in animal_info else "static/img/default-animal.jpg"
                    },
                    "submit_date": adoption["submission_date"].strftime("%d-%m-%Y") if "submission_date" in adoption else "Tidak tersedia",
                    "visit_date": adoption["visit_date"].strftime("%d-%m-%Y") if "visit_date" in adoption else "Tidak tersedia",
                    "status": adoption.get("status", "Pending")
                })

            return jsonify({"success": True, "message": list_adoptions})
        
        return render_template("user/adopt/adoption_info.html", title="Informasi Adopsi")
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
#* ==================== DETAIL ADOPSI ==================== #

@user_bp.route("/adoption_detail/<adoption_id>", methods=["GET"])
@login_required
def adoption_detail(adoption_id):
    try:
        adoption = mongo.db.form_adoption.find_one({"_id": ObjectId(adoption_id)})

        if not adoption:
            return jsonify({"success": False, "message": "Data adopsi tidak ditemukan"}), 404

        param_animal = adoption["animal"].get("name")
        animal = mongo.db.animals.find_one({"name": param_animal}) if param_animal else None

        if not animal:
            return jsonify({"success": False, "message": "Data hewan tidak ditemukan"}), 404

        # Format data yang akan dikirim ke frontend
        adoption_data = {
            "adopter": {
                "name": adoption["adopter"].get("name", ""),
                "datebirth": adoption["adopter"].get("datebirth", ""),
                "phone": adoption["adopter"].get("phone", ""),
                "email": adoption["adopter"].get("email", ""),
                "occupation": adoption["adopter"].get("occupation", ""),
                "address": adoption["adopter"].get("address", ""),
                "residence": adoption["adopter"].get("residence", ""),
                "reason": adoption["adopter"].get("reason", ""),
            },
            "animal": {
                "image": animal.get("image", ""),
                "name": animal.get("name", ""),
                "breed": animal.get("breed", ""),
                "sex": animal.get("sex", ""),
                "datebirth": animal.get("datebirth", ""),
                "desc": animal.get("desc", ""),
            },
            "status": adoption["status"],
            "submit_date": adoption.get("submission_date"),
            "visit_date": adoption.get("visit_date", "")
        }
        # print(178, adoption_data)
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": True, "adoption": adoption_data})

        return render_template("user/adopt/adoption_details.html", adoption_id=adoption_id, title="Detail Adopsi")

    except Exception as e:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "message": f"Terjadi kesalahan: {e}"}), 500
        return render_template("admin/data_adopsi.html")

#* ==================== TANGGAL KUNJUNGAN ==================== #

@user_bp.route("/tanggal_kunjungan", methods=["POST"])
@login_required
def tanggal_kunjungan():
    try:
        data = request.json
        adoption_id = data.get("adoption_id")
        visit_date = data.get("visit_date")

        print(1, visit_date)

        if not adoption_id or not visit_date:
            return jsonify({"success": False, "message": "Data tidak lengkap."}), 400

        # Konversi string menjadi format DateTime
        # visit_date = datetime.strptime(visit_date, "%Y-%m-%dT%H:%M")
        # visit_date = datetime.strptime(visit_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        visit_date_formatted = datetime.fromisoformat(visit_date.replace("Z", "+00:00"))

        print(2, visit_date_formatted)

        mongo.db.form_adoption.update_one(
            {"_id": ObjectId(adoption_id)},
            {"$set": {"visit_date": visit_date_formatted}}
        )

        return jsonify({"success": True, "message": "Tanggal kunjungan berhasil disimpan."})

    except ValueError:
        return jsonify({"success": False, "message": "Format tanggal tidak valid. Gunakan YYYY-MM-DD."}), 400

    except Exception as e:
        return jsonify({"success": False, "message": f"Terjadi kesalahan: {e}"}), 500
    
#* ==================== POSTING HEWAN ==================== #

@user_bp.route("/post_animals", methods=["GET", "POST"])
@login_required
def post_animals():
    try:
        user = get_current_user()
        print(248, user)
        if request.method == "GET":
            return render_template("user/animals/post_animals.html", title="Posting Hewan")

        json_data = request.form.get("data")
        if not json_data:
            return jsonify({"success": False, "message": "Data tidak ditemukan!"}), 400

        data = json.loads(json_data)
        print(257, data)
        file_foto = data.get("fotoHewan")

        if not file_foto:
            return jsonify({"success": False, "message": "Harap unggah foto hewan!"}), 400

        new_animal = {
            "name": data.get("namaHewan"),
            "breed": data.get("breedHewan"),
            "sex": data.get("jkHewan"),
            "datebirth": datetime.strptime(data.get("datebirthHewan"), "%Y-%m-%d"),
            "desc": data.get("desc"),
            "image": file_foto,  # Simpan sebagai Base64
            "address": {
                "street": data.get("street"),
                "city": data.get("city"),
                "province": data.get("province"),
                "postal_code": data.get("postal_code"),
            },
            "contact": {
                "name": data.get("namaPemilik"),
                "phone": data.get("noPemilik"),
                "email": data.get("emailPemilik"),
            },
            "status": {
                "steril_status": data.get("steril_status"),
                "vaccine_status": data.get("vaccine_status"),
                "microchip_status": data.get("microchip_status"),
                "adoption_status": False,
            },
            "created_at": datetime.utcnow()
        }

        result = mongo.db.animals.insert_one(new_animal)
        return jsonify({"success": True, "message": "Hewan berhasil diposting!", "animal_id": str(result.inserted_id)})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"success": False, "message": f"Terjadi kesalahan: {e}"}), 500