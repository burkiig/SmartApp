"""
Flask extension instances — initialized here, bound to app in create_app().
Import these from other modules to avoid circular imports.
"""

from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

cors = CORS()
jwt = JWTManager()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["500 per day", "100 per hour"],
    storage_uri="memory://",
)


def init_extensions(app):
    """Bind all extensions to the Flask app instance."""
    cors.init_app(
        app,
        supports_credentials=True,
        origins=app.config.get("CORS_ORIGINS", ["http://localhost:3000"]),
    )
    jwt.init_app(app)
    limiter.init_app(app)
