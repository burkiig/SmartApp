"""
Global error handlers — registered on the Flask app in create_app().
"""

from flask import jsonify
from shared.errors import APIError
from shared.logger import get_logger

log = get_logger()


def register_error_handlers(app):
    """Attach all error handlers to the Flask application."""

    @app.errorhandler(APIError)
    def handle_api_error(error):
        log.warning(f"[Error] APIError {error.status_code}: {error.message}")
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request", "status": 400}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Unauthorized", "status": 401}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Forbidden", "status": 403}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found", "status": 404}), 404

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return jsonify({"error": "Too many requests — slow down", "status": 429}), 429

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        log.error(f"[Error] Unexpected: {error}", exc_info=True)
        return jsonify({"error": "Internal server error", "status": 500}), 500
