"""
Authentication, autorization, and cryptographic utilities.

Handles password hashing, JWT (JSON Web Token) generation, and FastAPI
dependency injection for securing endpoints
"""

from datetime import UTC, datetime, timedelta

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from config import settings

# ==========================================
# CRYPTOGRAPHY & SECURITY SETUP
# ==========================================

password_hash = PasswordHash.recommended()


# Defines the exact endpoint the iOS app must hit to get a token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")


def hash_password(password: str) -> str:
    """Safely hashes a plaintext password before saving it to the database"""
    return password_hash.hash(password)


def verify_password(plain_password: str, hash_password: str) -> bool:
    """Compares a plaintext login attempt against the stored database hash."""
    return password_hash.verify(plain_password, hash_password)


# ==========================================
# JWT (JSON WEB TOKEN) MANAGEMENT
# ==========================================


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Generates a secure, time-limited JWT containing the user's ID payload.
    This token ascts as the user's digital passport for all future API requests.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(
        to_encode, settings.secret_key.get_secret_value(), algorithm=settings.algorithm
    )

    return encode_jwt


def verify_access_token(token: str) -> str | None:
    """
    Decodes the JWT to ensure it hasn't been tampered with and hasn't expired.
    Returns the user ID (subject) if valid or None if invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
            options={"require": ["exp", "sub"]},
        )
    except jwt.InvalidTokenError:
        return None
    else:
        return payload.get("sub")
