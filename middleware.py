from flask import session, redirect, url_for
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin":
            return redirect(url_for("user.home"))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Fungsi tambahan untuk mendapatkan informasi user yang sedang login."""
    if "user_id" in session:
        return {
            "id": session.get("user_id"),
            "name": session.get("username"),
            "email": session.get("email"),
            "role": session.get("role")
        }
    return None