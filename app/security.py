from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Necesitas iniciar sesión.", "warning")
            return redirect(url_for("auth.login"))

        # Validación por pestaña: URL debe portar token 'wid' igual a la sesión
        req_wid = request.args.get("wid")
        ses_wid = session.get("wid")
        if not req_wid or not ses_wid or req_wid != ses_wid:
            flash("Sesión no válida para esta pestaña. Vuelve a iniciar sesión.", "warning")
            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)
    return wrapped

def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("user_id"):
                flash("Necesitas iniciar sesión.", "warning")
                return redirect(url_for("auth.login"))

            req_wid = request.args.get("wid")
            ses_wid = session.get("wid")
            if not req_wid or not ses_wid or req_wid != ses_wid:
                flash("Sesión no válida para esta pestaña. Vuelve a iniciar sesión.", "warning")
                return redirect(url_for("auth.login"))

            if session.get("user_rol") not in roles:
                flash("No tienes permisos para esta acción.", "danger")
                return redirect(url_for("admin.dashboard", wid=session.get("wid")))

            return view(*args, **kwargs)
        return wrapped
    return decorator
