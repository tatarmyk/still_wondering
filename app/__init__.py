import os
import secrets

from flask import Flask
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

from app.config import Config

load_dotenv()

login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per hour"])


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    # Initialize extensions
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    csrf.init_app(app)
    limiter.init_app(app)

    # Database
    from app.models import init_db
    init_db(app)

    # Blueprints
    from app.auth import auth_bp
    from app.essays import essays_bp
    from app.comments import comments_bp
    from app.media import media_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(essays_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(media_bp)

    # Security headers
    @app.after_request
    def set_security_headers(response):
        nonce = getattr(app.jinja_env.globals.get("csp_nonce", None), "__func__", None)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' https: data:; "
            "frame-src https://www.youtube.com https://www.youtube-nocookie.com; "
            "media-src 'self' https:; "
            "object-src 'none'; "
            "base-uri 'self';"
        )
        return response

    # Inject csp_nonce into templates (for future use with nonces)
    @app.context_processor
    def inject_globals():
        return {"csp_nonce": secrets.token_hex(16)}

    return app
