import os
import uuid
from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, current_app,
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from app import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__, template_folder="../templates/auth")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _allowed_file(filename: str) -> bool:
    """Return True if the file extension is in the allow-list."""
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", set())
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def _save_photo(file) -> str | None:
    """Persist the uploaded photo and return the URL path, or None on failure."""
    if not file or file.filename == "":
        return None
    if not _allowed_file(file.filename):
        flash("Photo must be a PNG, JPG, JPEG, GIF, or WEBP file.", "warning")
        return None

    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, unique_name))
    return url_for("static", filename=f"img/uploads/{unique_name}")


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name  = request.form.get("last_name", "").strip()
        email      = request.form.get("email", "").strip().lower()
        password   = request.form.get("password", "")
        phone      = request.form.get("phone", "").strip()
        city       = request.form.get("city", "").strip()
        country    = request.form.get("country", "").strip()
        photo_file = request.files.get("photo")

        # --- Validation ---
        if not first_name or not last_name:
            flash("First and last name are required.", "danger")
            return render_template("register.html")
        if not email or "@" not in email:
            flash("A valid email address is required.", "danger")
            return render_template("register.html")
        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return render_template("register.html")
        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists. Please log in.", "warning")
            return redirect(url_for("auth.login"))

        photo_url = _save_photo(photo_file)

        user = User(
            name=f"{first_name} {last_name}",
            email=email,
            password_hash=generate_password_hash(password),
            photo_url=photo_url,
            phone=phone or None,
            city=city or None,
            country=country or None,
        )
        db.session.add(user)
        db.session.commit()

        flash("Account created! You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template("login.html")

        login_user(user, remember=remember)
        next_page = request.args.get("next")
        return redirect(next_page or url_for("home"))

    return render_template("login.html")


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
