"""
Security and password hashing utilities.
"""

import hashlib
import os


def hash_password(password: str, salt: bytes | None = None) -> str:
    """Hashes a plain-text password using SHA-256 with a secure random salt.

    Args:
        password: Plain text password string.
        salt: Optional salt bytes. Generated automatically if not provided.

    Returns:
        Combined string in format 'salt_hex:hash_hex'.
    """
    if not salt:
        salt = os.urandom(16)

    hash_obj = hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=password.encode("utf-8"),
        salt=salt,
        iterations=100_000,
    )
    return f"{salt.hex()}:{hash_obj.hex()}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verifies a plain-text password against a stored salt:hash string.

    Args:
        plain_password: Plain text password input to verify.
        stored_hash: Previously generated 'salt_hex:hash_hex' string.

    Returns:
        True if password matches, False otherwise.
    """
    try:
        salt_hex, _ = stored_hash.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        computed = hash_password(plain_password, salt=salt)
        return computed == stored_hash
    except (ValueError, AttributeError):
        return False
