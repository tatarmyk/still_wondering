from flask import Blueprint, render_template, redirect, url_for, request, flash, make_response
from flask_login import login_required, current_user

from app.models import get_db, Essay
from app.rendering import render_essay

essays_bp = Blueprint("essays", __name__)


@essays_bp.route("/")
def index():
    db = get_db()
    try:
        essays = (
            db.query(Essay)
            .filter_by(published=True)
            .order_by(Essay.created_at.desc())
            .all()
        )
        return render_template("index.html", essays=essays)
    finally:
        db.close()


@essays_bp.route("/essay/<int:essay_id>")
def view(essay_id):
    db = get_db()
    try:
        essay = db.query(Essay).get(essay_id)
        if not essay or (not essay.published and not current_user.is_authenticated):
            return render_template("404.html"), 404

        from app.models import Comment
        comments = (
            db.query(Comment)
            .filter_by(essay_id=essay_id)
            .order_by(Comment.created_at.asc())
            .all()
        )

        rendered_body = render_essay(essay.body_md)
        eye_cookie = request.cookies.get(f"eye_{essay_id}")

        return render_template(
            "essay.html",
            essay=essay,
            rendered_body=rendered_body,
            comments=comments,
            has_eyed=bool(eye_cookie),
        )
    finally:
        db.close()


@essays_bp.route("/essay/<int:essay_id>/eye", methods=["POST"])
def eye(essay_id):
    """Record a read acknowledgment (eye). One per browser via cookie."""
    cookie_key = f"eye_{essay_id}"
    if request.cookies.get(cookie_key):
        return redirect(url_for("essays.view", essay_id=essay_id))

    db = get_db()
    try:
        essay = db.query(Essay).get(essay_id)
        if not essay:
            return render_template("404.html"), 404
        essay.eye_count = (essay.eye_count or 0) + 1
        db.commit()
    finally:
        db.close()

    response = make_response(redirect(url_for("essays.view", essay_id=essay_id)))
    response.set_cookie(cookie_key, "1", max_age=60 * 60 * 24 * 365, httponly=True, samesite="Lax")
    return response


# --- Author-only routes ---

@essays_bp.route("/drafts")
@login_required
def drafts():
    db = get_db()
    try:
        essays = (
            db.query(Essay)
            .order_by(Essay.created_at.desc())
            .all()
        )
        return render_template("drafts.html", essays=essays)
    finally:
        db.close()


@essays_bp.route("/essay/new", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body_md = request.form.get("body_md", "")
        published = "publish" in request.form

        if not title:
            flash("Title is required.", "error")
            return render_template("editor.html", title=title, body_md=body_md)

        db = get_db()
        try:
            essay = Essay(title=title, body_md=body_md, published=published)
            db.add(essay)
            db.commit()
            db.refresh(essay)
            flash("Essay saved.", "success")
            return redirect(url_for("essays.view", essay_id=essay.id))
        finally:
            db.close()

    return render_template("editor.html", title="", body_md="")


@essays_bp.route("/essay/<int:essay_id>/edit", methods=["GET", "POST"])
@login_required
def edit(essay_id):
    db = get_db()
    try:
        essay = db.query(Essay).get(essay_id)
        if not essay:
            return render_template("404.html"), 404

        if request.method == "POST":
            essay.title = request.form.get("title", "").strip()
            essay.body_md = request.form.get("body_md", "")
            essay.published = "publish" in request.form

            if not essay.title:
                flash("Title is required.", "error")
                return render_template("editor.html", title=essay.title, body_md=essay.body_md, essay=essay)

            db.commit()
            flash("Essay updated.", "success")
            return redirect(url_for("essays.view", essay_id=essay.id))

        return render_template("editor.html", title=essay.title, body_md=essay.body_md, essay=essay)
    finally:
        db.close()


@essays_bp.route("/essay/<int:essay_id>/delete", methods=["POST"])
@login_required
def delete(essay_id):
    db = get_db()
    try:
        essay = db.query(Essay).get(essay_id)
        if essay:
            db.delete(essay)
            db.commit()
            flash("Essay deleted.", "success")
    finally:
        db.close()
    return redirect(url_for("essays.drafts"))
