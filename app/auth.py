from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app import login_manager, limiter
from app.models import get_db, Author

auth_bp = Blueprint("auth", __name__)
ph = PasswordHasher()


@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    try:
        return db.query(Author).get(int(user_id))
    finally:
        db.close()


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()
        try:
            author = db.query(Author).filter_by(username=username).first()
            if author:
                try:
                    ph.verify(author.password_hash, password)
                    login_user(author)
                    next_page = request.args.get("next")
                    # Only allow relative redirects (prevent open redirect)
                    if next_page and not next_page.startswith("/"):
                        next_page = None
                    return redirect(next_page or url_for("essays.index"))
                except VerifyMismatchError:
                    pass
        finally:
            db.close()

        flash("Invalid credentials.", "error")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("essays.index"))
