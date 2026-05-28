from flask import Blueprint, request, redirect, url_for, flash, jsonify
from flask_login import login_required

from app import limiter, csrf
from app.models import get_db, Comment, hash_ip

comments_bp = Blueprint("comments", __name__)

MAX_COMMENT_LENGTH = 2000


@comments_bp.route("/essay/<int:essay_id>/comment", methods=["POST"])
@limiter.limit("10 per minute")
def create(essay_id):
    section_id = request.form.get("section_id", "").strip()
    author_name = request.form.get("author_name", "").strip()[:80]
    body = request.form.get("body", "").strip()[:MAX_COMMENT_LENGTH]

    if not section_id or not body:
        flash("Comment body is required.", "error")
        return redirect(url_for("essays.view", essay_id=essay_id))

    ip = request.remote_addr or "unknown"

    db = get_db()
    try:
        comment = Comment(
            essay_id=essay_id,
            section_id=section_id,
            author_name=author_name,
            body=body,
            ip_hash=hash_ip(ip),
        )
        db.add(comment)
        db.commit()
    finally:
        db.close()

    return redirect(url_for("essays.view", essay_id=essay_id) + f"#{section_id}")


@comments_bp.route("/comment/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete(comment_id):
    db = get_db()
    try:
        comment = db.query(Comment).get(comment_id)
        if comment:
            essay_id = comment.essay_id
            db.delete(comment)
            db.commit()
            return redirect(url_for("essays.view", essay_id=essay_id))
    finally:
        db.close()
    return redirect(url_for("essays.index"))
