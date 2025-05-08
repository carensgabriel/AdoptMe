from bson import ObjectId
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session
from database import mongo
from middleware import admin_required, login_required

admin_bp = Blueprint("admin", __name__)

def convert_for_json(data):
    if isinstance(data, list):
        return [convert_for_json(item) for item in data]
    elif isinstance(data, dict):
        return {
            key: convert_for_json(value)
            for key, value in data.items()
        }
    elif isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, datetime):
        return data.isoformat()
    else:
        return data

@admin_bp.route("/admin/dashboard")
@admin_required
@login_required
def dashboard():

    username = session.get('username', 'Admin')
    adoptions = mongo.db.form_adoption.find()

    return render_template("admin/dashboard.html", title="Dashboard", auth={'username': username}, adoptions=adoptions)

#* ========================= DATA ADOPSI ========================= #

# ? ========================= GET DATA LIST ADOPSI =========================
@admin_bp.route("/admin/adoption", methods=["GET"])
@admin_required
@login_required
def adoptions_list():
    try:
        username = session.get('username', 'Admin')
        adoptions = list(mongo.db.form_adoption.find({}))
        
        for adoption in adoptions:
            adoption['_id'] = str(adoption['_id'])

        adoptions = convert_for_json(adoptions)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": True, "data": adoptions})

    except Exception as e:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500
        return render_template("admin/data_adopsi.html", auth={'username': username}, adoptions=[])

# ? ========================= GET DATA ADOPSI DETAILS =========================
@admin_bp.route("/admin/adoption/<adoption_id>", methods=["GET"])
@admin_required
@login_required
def adoption_detail(adoption_id):
    try:
        adoption = mongo.db.form_adoption.find_one({"_id": ObjectId(adoption_id)})
        if not adoption:
            return jsonify({"success": False, "message": "Adopsi tidak ditemukan"}), 404

        adoption["_id"] = str(adoption["_id"])
        adoption["adopter"] = adoption.get("adopter", {})
        adoption["animal"] = adoption.get("animal", {})
        adoption["emergency_contact"] = adoption.get("emergency_contact", {})

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            adoption_json = convert_for_json(adoption)
            return jsonify({"success": True, "data": adoption_json})

        return render_template("admin/adoption_details.html", title="Detail Adopsi", adoption=adoption)

    except Exception as e:
        print("error:", e)
        return jsonify({"success": False, "message": str(e)}), 500
    
# ? ========================= UPDATE STATUS ADOPSI =========================
@admin_bp.route("/admin/adoption/update_status", methods=["POST"])
@admin_required
@login_required
def update_status():
    try:
        adoption_id = request.form['adoption_id']
        new_status = request.form['status']

        result = mongo.db.form_adoption.update_one(
            {"_id": ObjectId(adoption_id)},
            {"$set": {"status": new_status}}
        )
        
        if result.modified_count > 0:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": "Tidak ada perubahan pada status."})
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
#* ========================= AKHIR DATA ADOPSI ========================= #    

#* ========================= DATA HEWAN ========================= #

# ? ========================= GET DATA ANIMAL LIST =========================
@admin_bp.route("/admin/animals-list", methods=["GET"])
@admin_required
@login_required
def animals_list():
    if "X-Requested-With" in request.headers and request.headers["X-Requested-With"] == "XMLHttpRequest":
        try:
            animals = list(mongo.db.animals.find())
            for animal in animals:
                animal["_id"] = str(animal["_id"])
                animal["image"] = animal.get("image", "/static/images/default-animal.jpg")
            
            return jsonify({"success": True, "data": animals})
        
        except Exception as e:
            print("Error:", e)
            return jsonify({"success": False, "message": "Terjadi kesalahan server!"}), 500

    username = session.get("username", "Admin")
    return render_template("admin/data_hewan.html", title="Data Hewan", auth={"username": username})

# ? ========================= GET DATA ANIMAL DETAILS =========================
@admin_bp.route("/admin/animal-details/<animal_id>", methods=["GET"])
@admin_required
@login_required
def animal_details(animal_id):
    try:
        animal = mongo.db.animals.find_one({"_id": ObjectId(animal_id)})
        if not animal:
            return jsonify({"success": False, "message": "Adopsi tidak ditemukan"}), 404

        animal["_id"] = str(animal["_id"])

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(animal)

        return render_template("admin/animal_details.html", title="Detail Hewan", animal=animal)

    except Exception as e:
        print("Error:", e)
        return render_template("admin/animal_details.html", error="Terjadi kesalahan server.")

# ? ========================= UPDATE DATA ANIMAL =========================
@admin_bp.route("/admin/animal-update/<animal_id>", methods=["POST"])
@admin_required
@login_required
def animal_update(animal_id):
    try:
        data = request.get_json()

        if 'datebirth' in data and data['datebirth']:
            # Mengonversi string tanggal dari format 'YYYY-MM-DD' menjadi objek datetime
            data['datebirth'] = datetime.strptime(data['datebirth'], '%Y-%m-%dT%H:%M:%S.%fZ')

        mongo.db.animals.update_one(
            {"_id": ObjectId(animal_id)},
            {"$set": data}
        )
        return jsonify({"success": True, "message": "Data berhasil diperbarui."}), 200
    
    except Exception as e:
        print("Error:", e)
        return jsonify({"success": False, "message": str(e)}), 500

#* ========================= AKHIR DATA HEWAN ========================= #

#* ========================= DATA USER ========================= #

# ? ========================= GET DATA USER =========================
@admin_bp.route("/admin/users-list", methods=["GET"])
@admin_required
@login_required
def users_list():
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        try:
            users = list(mongo.db.users.find({}, {"_id": 1, "username": 1, "email": 1, "role": 1}))
            for user in users:
                user["_id"] = str(user["_id"])
            
            return jsonify({"success": True, "data": users})
        
        except Exception as e:
            print("Error:", e)
            return jsonify({"success": False, "message": "Terjadi kesalahan server!"}), 500

    username = session.get("username", "Admin")
    return render_template("admin/data_user.html", title="Data User", auth={"username": username})

# ? ========================= UPDATE USER =========================
@admin_bp.route("/admin/users/<user_id>/edit", methods=["PUT"])
@admin_required
@login_required
def edit_user(user_id):
    try:
        data = request.json
        result = mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": data})

        if result.modified_count > 0:
            return jsonify({"success": True, "message": "User berhasil diperbarui"})
        else:
            return jsonify({"success": False, "message": "Tidak ada perubahan"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
# ? ========================= DELETE USER =========================
@admin_bp.route("/admin/users/<user_id>/delete", methods=["DELETE"])
@admin_required
@login_required
def delete_user(user_id):
    try:
        result = mongo.db.users.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count > 0:
            return jsonify({"success": True, "message": "User berhasil dihapus"})
        else:
            return jsonify({"success": False, "message": "User tidak ditemukan"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

#* ========================= AKHIR DATA USER ========================= #        