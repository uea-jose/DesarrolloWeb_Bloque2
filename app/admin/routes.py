
from flask import render_template, session
from . import admin_bp
from app.security import login_required, role_required

@admin_bp.route("/dashboard")
@login_required
@role_required('admin')
def dashboard():
    return render_template("admin/dashboard.html",
        user_nombre=session.get("user_nombre"),
        user_username=session.get("user_username"),
        user_rol=session.get("user_rol"))
