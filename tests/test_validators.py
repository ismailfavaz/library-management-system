"""
Unit tests for input validation functions.
"""

import pytest

from src.library.exceptions import InvalidEmailError, InvalidISBNError, ValidationError
from src.library.utils.validators import (
    validate_email,
    validate_isbn,
    validate_non_empty_string,
    validate_positive_int,
)


def test_validate_isbn_valid_cases() -> None:
    """Verify valid ISBN-10 and ISBN-13 strings normalize correctly."""
    # Valid ISBN-10
    assert validate_isbn("0-306-40615-2") == "0306406152"
    assert validate_isbn("0306406152") == "0306406152"
    assert validate_isbn("0-8044-2957-X") == "080442957X"

    # Valid ISBN-13
    assert validate_isbn("978-3-16-148410-0") == "9783161484100"
    assert validate_isbn("9783161484100") == "9783161484100"


def test_validate_isbn_invalid_cases() -> None:
    """Verify invalid ISBN strings trigger InvalidISBNError."""
    with pytest.raises(InvalidISBNError):
        validate_isbn("12345")

    with pytest.raises(InvalidISBNError):
        validate_isbn("0-306-40615-9")  # Bad ISBN-10 checksum

    with pytest.raises(InvalidISBNError):
        validate_isbn("978-3-16-148410-9")  # Bad ISBN-13 checksum


def test_validate_email_valid_and_invalid() -> None:
    """Verify email format validation."""
    assert validate_email("  User@Example.COM ") == "user@example.com"

    with pytest.raises(InvalidEmailError):
        validate_email("plainaddress")

    with pytest.raises(InvalidEmailError):
        validate_email("@missinguser.com")

    with pytest.raises(InvalidEmailError):
        validate_email("user@.com")


def test_validate_positive_int() -> None:
    """Verify positive integer conversion and validation."""
    assert validate_positive_int(10, "copies") == 10
    assert validate_positive_int("5", "year") == 5

    with pytest.raises(ValidationError):
        validate_positive_int(0, "copies")

    with pytest.raises(ValidationError):
        validate_positive_int("-3", "copies")

    with pytest.raises(ValidationError):
        validate_positive_int("abc", "copies")


def test_validate_non_empty_string() -> None:
    """Verify string non-emptiness validation."""
    assert validate_non_empty_string("  Clean Code  ", "Title") == "Clean Code"

    with pytest.raises(ValidationError):
        validate_non_empty_string("", "Title")

    with pytest.raises(ValidationError):
        validate_non_empty_string("   ", "Title")
