import os
import secrets

from flask import Blueprint, request, jsonify, url_for, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename

from app.config import Config

media_bp = Blueprint("media", __name__)


def allowed_file(filename: str) -> bool:
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@media_bp.route("/upload", methods=["POST"])
@login_required
def upload():
    """Upload an image file. Returns JSON with the URL."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed. Use: png, jpg, gif, webp"}), 400

    # Check file size (read up to limit + 1 byte)
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)

    if size > Config.MAX_UPLOAD_SIZE:
        return jsonify({"error": "File too large. Maximum 5MB."}), 400

    # Generate random filename to prevent enumeration
    ext = file.filename.rsplit(".", 1)[1].lower()
    random_name = secrets.token_hex(16) + "." + ext
    save_path = os.path.join(Config.UPLOAD_FOLDER, random_name)

    file.save(save_path)

    file_url = url_for("static", filename=f"uploads/{random_name}")
    return jsonify({"url": file_url}), 201
