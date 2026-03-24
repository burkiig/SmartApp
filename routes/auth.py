"""
Authentication routes.
POST /api/login          — obtain access + refresh tokens
POST /api/logout         — client-side token invalidation
POST /api/auth/refresh   — exchange refresh token for new access token
GET  /api/users          — admin: list all users
POST /api/users          — admin: create user
DELETE /api/users/<username> — admin: delete user
POST /api/users/push-token  — save Expo push token (any authenticated user)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from werkzeug.security import generate_password_hash, check_password_hash

from database.factory import get_db
from extensions import limiter
from middleware.auth_middleware import require_role
from shared.errors import ValidationError, APIError
from shared.logger import get_logger

log = get_logger()
auth_bp = Blueprint("auth", __name__, url_prefix="/api")


# ── Login ──────────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        raise ValidationError("username ve password gerekli")

    db = get_db()
    user = db.get_user(username)

    if not user or not check_password_hash(user.get("password", ""), password):
        log.warning(f"[Auth] Failed login: {username}")
        return jsonify({"success": False, "message": "Kullanıcı adı veya şifre hatalı"}), 401

    identity = {"username": username, "role": user.get("role", "student")}
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    user_data = {k: v for k, v in user.items() if k != "password"}
    log.info(f"[Auth] Login: {username}")
    return jsonify({
        "success": True,
        "message": "Giriş başarılı",
        "user": user_data,
        "access_token": access_token,
        "refresh_token": refresh_token,
    })


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    identity = get_jwt_identity()
    log.info(f"[Auth] Logout: {identity.get('username')}")
    return jsonify({"success": True, "message": "Çıkış başarılı"})


@auth_bp.route("/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    log.info(f"[Auth] Token refresh: {identity.get('username')}")
    return jsonify({"success": True, "access_token": access_token})


# ── User management (admin) ────────────────────────────────────────────────────

@auth_bp.route("/users", methods=["GET"])
@jwt_required()
@require_role("admin")
def get_users():
    db = get_db()
    users = db.get_users()
    return jsonify({
        "success": True,
        "users": [{k: v for k, v in u.items() if k != "password"} for u in users],
    })


@auth_bp.route("/users", methods=["POST"])
@jwt_required()
@require_role("admin")
def add_user():
    data = request.get_json() or {}
    required = ["username", "name", "email", "role", "password"]
    if not all(data.get(f) for f in required):
        return jsonify({"success": False, "message": "Tüm alanlar gerekli"}), 400

    db = get_db()
    if db.get_user(data["username"]):
        return jsonify({"success": False, "message": "Kullanıcı adı zaten kullanılıyor"}), 409

    user_data = {
        "username": data["username"],
        "password": generate_password_hash(data["password"]),
        "role": data["role"],
        "name": data["name"],
        "email": data["email"],
    }
    if data["role"] == "instructor":
        user_data["department"] = data.get("department", "")
    elif data["role"] == "student":
        user_data["student_id"] = data.get("student_id", "")

    created = db.create_user(user_data)
    log.info(f"[Auth] User created: {data['username']} ({data['role']})")
    return jsonify({
        "success": True,
        "message": "Kullanıcı oluşturuldu",
        "user": {k: v for k, v in created.items() if k != "password"},
    })


@auth_bp.route("/users/<username>", methods=["DELETE"])
@jwt_required()
@require_role("admin")
def delete_user(username):
    db = get_db()
    if not db.delete_user(username):
        return jsonify({"success": False, "message": "Kullanıcı bulunamadı"}), 404
    log.info(f"[Auth] User deleted: {username}")
    return jsonify({"success": True, "message": "Kullanıcı silindi"})


# ── Push token ─────────────────────────────────────────────────────────────────

@auth_bp.route("/users/push-token", methods=["POST"])
@jwt_required()
def save_push_token():
    data = request.get_json() or {}
    push_token = data.get("push_token")
    if not push_token:
        return jsonify({"success": False, "message": "push_token gerekli"}), 400

    identity = get_jwt_identity()
    username = identity.get("username")
    db = get_db()

    user = db.get_user(username)
    if user:
        db.update_user(username, {"push_token": push_token})
        if user.get("role") == "student":
            student_id = user.get("student_id")
            if student_id and db.get_student(student_id):
                db.update_student(student_id, {"push_token": push_token})

    log.info(f"[Auth] Push token saved: {username}")
    return jsonify({"success": True, "message": "Push token kaydedildi"})
