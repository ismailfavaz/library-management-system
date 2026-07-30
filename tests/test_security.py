"""
Unit tests for password hashing and verification functions.
"""

from src.library.utils.security import hash_password, verify_password


def test_hash_and_verify_password() -> None:
    """Verify password hashing creates valid hash format and verifies correctly."""
    plain_pwd = "SecretPassword123!"
    hashed = hash_password(plain_pwd)

    assert ":" in hashed
    assert verify_password(plain_pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_verify_invalid_hash_format() -> None:
    """Verify verify_password returns False for malformed hashes."""
    assert verify_password("any_password", "invalid_hash_string") is False
    assert verify_password("any_password", "") is False
