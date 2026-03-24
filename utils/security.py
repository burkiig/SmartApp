"""
Security utility helpers.
"""

import os
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(plain: str) -> str:
    """
    Hash a plain-text password.
    Uses werkzeug pbkdf2:sha256 by default.
    To switch to bcrypt: generate_password_hash(plain, method='bcrypt')
    (requires: pip install bcrypt)
    """
    return generate_password_hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain-text password against a stored hash."""
    return check_password_hash(hashed, plain)


def generate_secret_key(length: int = 32) -> str:
    """Generate a cryptographically secure random secret key."""
    return os.urandom(length).hex()
