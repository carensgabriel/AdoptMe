from bson import ObjectId
from flask import Blueprint, render_template, jsonify, url_for, redirect, request, session
from database import mongo
from middleware import login_required

user_bp = Blueprint("user", __name__)

# ============================================================ #

@user_bp.route("/home")
def home():
    return render_template("home.html")  # Halaman home untuk user

# ============================================================ #

@user_bp.route("/profile")
def user_profile():
    return render_template("user/user_profile.html")  # Halaman home untuk user