from flask import Blueprint, redirect, render_template, jsonify, url_for, request, session
from bson.objectid import ObjectId
from database import mongo
from datetime import datetime
from middleware import *

animal_bp = Blueprint("animal", __name__)

# ============================================================ #

def calculate_age(datebirth):
    """Menghitung usia dari tanggal lahir"""
    if not datebirth:
        return "Usia tidak tersedia"

    if isinstance(datebirth, str):  
        birth_date = datetime.strptime(datebirth, "%Y-%m-%d")
    elif isinstance(datebirth, datetime):  
        birth_date = datebirth
    else:
        return "Format tanggal tidak valid"

    today = datetime.today()
    years = today.year - birth_date.year
    months = today.month - birth_date.month
    if today.day < birth_date.day:
        months -= 1
    if months < 0:
        years -= 1
        months += 12

    return f"{years} Tahun, {months} Bulan" if years > 0 else f"{months} Bulan"

# ============================================================ #

@animal_bp.route("/animals")
def animals():
    return render_template("user/animals/animals_list.html", title="Daftar Hewan")

# ============================================================ #

#* get animals_list *#
@animal_bp.route("/get_animals", methods=["GET"])
def get_animals():
    try:
        species = request.args.get("species", "").strip()
        location = request.args.get("location", "").strip()
        shelter = request.args.get("shelter", "").strip()

        query = {}

        if species:
            query["species"] = species
        if location:
            query["address.city"] = {"$regex": location, "$options": "i"}
        if shelter:
            query["shelter_name"] = {"$regex": shelter, "$options": "i"}

        animals = list(mongo.db.animals.find(query, {"_id": 1, "name": 1, "contact.name": 1, "image": 1, "sex": 1, "address.city" : 1}))

        for animal in animals:
            animal["_id"] = str(animal["_id"])

        return jsonify({"animals": animals})
    
    except Exception as e:
        print(e)
        return jsonify({'message': 'Terjadi Kesalahan Server!'}), 500


# ============================================================ #

# * DETAILS * #
@animal_bp.route("/details/<animal_id>")
def animal_details(animal_id):
    try:
        """Render halaman detail hewan atau kembalikan data JSON berdasarkan request."""

        if request.args.get("format") == "json":
            animal = mongo.db.animals.find_one({"_id": ObjectId(animal_id)})

            if not animal:
                return jsonify({"error": "Hewan tidak ditemukan"}), 404

            animal["_id"] = str(animal["_id"])
            return jsonify(animal)

        return render_template("user/animals/animal_details.html", title="Detail Hewan", animal_id=animal_id)
    
    except Exception as e:
        print(e)
        return jsonify({'message': 'Terjadi Kesalahan Server!'}), 500

# ============================================================ #

# * ADOPSI * #
@animal_bp.route("/adopt/<animal_id>")
@login_required
def form_adopsi(animal_id):
    try:
        animal = mongo.db.animals.find_one({"_id": ObjectId(animal_id)})
        if not animal:
            return "Hewan tidak ditemukan", 404
        return render_template("user/adopt/form_adopsi.html", title="Form Adopsi", animal=animal)
    
    except Exception as e:
        print(e)
        return jsonify({'message': 'Terjadi Kesalahan Server!'}), 500

# ============================================================ #

# * COMPARE * #
@animal_bp.route("/compare", methods=["GET"])
def select_animals():
    try:

        """Menampilkan daftar hewan untuk dibandingkan"""
        animals = list(mongo.db.animals.find({}, {"_id": 1, "name": 1, "breed": 1, "datebirth": 1, "image": 1}))

        for animal in animals:
            animal["_id"] = str(animal["_id"])
            animal["datebirth"] = calculate_age(animal.get("datebirth"))

        return render_template("user/compare/select_animals.html", title="Bandingkan Hewan", animals=animals)
    
    except Exception as e:
        print(e)
        return jsonify({'message': 'Terjadi Kesalahan Server!'}), 500

# ============================================================ #

# * COMPARE SELECTED * #
@animal_bp.route("/compare/selected_animals", methods=["GET", "POST"])
@login_required
def compare_selected_animals():
    try:
        
        if request.method == "POST":
            try:
                data = request.get_json()
                selected_ids = data.get("selected_animals", [])

                if not selected_ids:
                    return jsonify({"success": False, "message": "Tidak ada hewan yang dipilih!"}), 400

                selected_animals = list(mongo.db.animals.find(
                    {"_id": {"$in": [ObjectId(animal_id) for animal_id in selected_ids]}}
                ))

                for animal in selected_animals:
                    animal["_id"] = str(animal["_id"])
                    animal["datebirth"] = calculate_age(animal.get("datebirth"))

                return jsonify({"success": True, "animals": selected_animals})

            except Exception as e:
                return jsonify({"success": False, "message": str(e)}), 500

        return render_template("user/compare/selected_animals.html")
    
    except Exception as e:
        print(e)
        return jsonify({'message': 'Terjadi Kesalahan Server!'}), 500