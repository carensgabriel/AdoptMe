from flask import Blueprint, render_template, session, redirect, url_for
from database import mongo
from middleware import admin_required

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("auth.login"))  # Jika bukan admin, kembali ke login
    return render_template("admin/dashboard.html")  # Halaman dashboard admin