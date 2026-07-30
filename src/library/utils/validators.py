"""
Input validation utilities for domain entities and CLI inputs.
"""

import re
from src.library.exceptions import InvalidEmailError, InvalidISBNError, ValidationError

# RFC 5322 compliant regex pattern for basic email format checking
_EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def validate_isbn(isbn: str) -> str:
    """Validates ISBN-10 or ISBN-13 string format.

    Args:
        isbn: The ISBN string to validate (may contain hyphens or spaces).

    Returns:
        Cleaned, hyphen-free upper-case ISBN string.

    Raises:
        InvalidISBNError: If the ISBN format is invalid.
    """
    if not isbn or not isinstance(isbn, str):
        raise InvalidISBNError(str(isbn))

    clean_isbn = isbn.replace("-", "").replace(" ", "").strip().upper()

    if len(clean_isbn) == 10:
        # Check standard ISBN-10: first 9 chars digits, last digit or 'X'
        if not (clean_isbn[:9].isdigit() and (clean_isbn[9].isdigit() or clean_isbn[9] == "X")):
            raise InvalidISBNError(isbn)
        # Checksum calculation for ISBN-10
        total = sum((10 - i) * (10 if char == "X" else int(char)) for i, char in enumerate(clean_isbn))
        if total % 11 != 0:
            raise InvalidISBNError(isbn)
    elif len(clean_isbn) == 13:
        # Check standard ISBN-13: 13 digits
        if not clean_isbn.isdigit():
            raise InvalidISBNError(isbn)
        # Checksum calculation for ISBN-13
        total = sum(int(char) * (1 if i % 2 == 0 else 3) for i, char in enumerate(clean_isbn))
        if total % 10 != 0:
            raise InvalidISBNError(isbn)
    else:
        raise InvalidISBNError(isbn)

    return clean_isbn


def validate_email(email: str) -> str:
    """Validates email format.

    Args:
        email: Email address string.

    Returns:
        Cleaned lowercase email string.

    Raises:
        InvalidEmailError: If the email address format is invalid.
    """
    if not email or not isinstance(email, str):
        raise InvalidEmailError(str(email))

    clean_email = email.strip().lower()
    if not _EMAIL_REGEX.match(clean_email):
        raise InvalidEmailError(email)

    return clean_email


def validate_positive_int(value: int | str, field_name: str) -> int:
    """Validates that a given input is a positive integer greater than zero.

    Args:
        value: Numeric value or integer string.
        field_name: Human-readable field identifier for error messages.

    Returns:
        Integer representation.

    Raises:
        ValidationError: If value is not a positive integer.
    """
    try:
        val = int(value)
        if val <= 0:
            raise ValueError()
        return val
    except (ValueError, TypeError):
        raise ValidationError(f"Field '{field_name}' must be a positive integer greater than zero. Got: '{value}'.")


def validate_non_empty_string(value: str, field_name: str) -> str:
    """Validates that a string is non-empty and non-whitespace.

    Args:
        value: Input string.
        field_name: Human-readable field name for error output.

    Returns:
        Stripped non-empty string.

    Raises:
        ValidationError: If string is empty or contains only whitespace.
    """
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"Field '{field_name}' cannot be empty.")
    return value.strip()


def validate_phone_number(phone: str) -> str:
    """Validates and normalizes phone number input.

    Args:
        phone: Raw phone number string (e.g. '+1 (555) 019-2834').

    Returns:
        Normalized phone string.

    Raises:
        ValidationError: If the phone number is invalid.
    """
    if not isinstance(phone, str) or not phone.strip():
        raise ValidationError("Phone number cannot be empty.")

    cleaned = re.sub(r"[\s\-\(\)\.]", "", phone.strip())
    # Allow leading '+' followed by 7 to 15 digits
    if not re.match(r"^\+?[0-9]{7,15}$", cleaned):
        raise ValidationError(f"Invalid phone number format: '{phone}'. Must contain 7 to 15 digits.")

    return cleaned

