from bson import ObjectId
from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session
from database import mongo
from middleware import admin_required

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/dashboard")
def dashboard():

    username = session.get('username', 'Admin')
    adoptions = mongo.db.form_adoption.find()

    return render_template("admin/dashboard.html", auth={'username': username}, adoptions=adoptions)

#* ========================= GET DATA ADOPSI ========================= #

@admin_bp.route("/adoptions", methods=["GET"])
def get_adoptions():
    try:
        adoptions = list(mongo.db.form_adoption.find({}))
        
        for adoption in adoptions:
            adoption['_id'] = str(adoption['_id'])

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": True, "data": adoptions})
        
        return render_template("admin/data_adopsi.html", adoptions=adoptions)

    except Exception as e:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500
        return render_template("admin/data_adopsi.html", adoptions=[])

    
#* ========================= GET DATA DETAIL ADOPSI ========================= #

@admin_bp.route("/adoption/<adoption_id>", methods=["GET"])
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
            return jsonify({"success": True, "data": adoption})

        return render_template("admin/adoption_detail.html", adoption=adoption)

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
#* ========================= UPDATE STATUS ADOPSI ========================= #

@admin_bp.route("/adoption/update_status", methods=["POST"])
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