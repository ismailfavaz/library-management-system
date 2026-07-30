"""
Unit tests for logger utilities and exception hierarchy.
"""

import logging
from pathlib import Path
import pytest

from src.library.exceptions import (
    BookNotAvailableError,
    BookNotFoundError,
    InvalidEmailError,
    InvalidISBNError,
    LibraryError,
    UserNotFoundError,
)
from src.library.utils.logger import get_logger, setup_logger


def test_exception_hierarchy() -> None:
    """Verify inheritance and message formatting of domain exceptions."""
    err = BookNotFoundError("12345")
    assert isinstance(err, LibraryError)
    assert "12345" in str(err)
    assert err.identifier == "12345"

    user_err = UserNotFoundError(99)
    assert isinstance(user_err, LibraryError)
    assert "99" in str(user_err)

    isbn_err = InvalidISBNError("INVALID-ISBN")
    assert "INVALID-ISBN" in str(isbn_err)

    email_err = InvalidEmailError("bad@email")
    assert "bad@email" in str(email_err)

    avail_err = BookNotAvailableError("Clean Code")
    assert "Clean Code" in str(avail_err)


def test_logger_setup(tmp_path: Path) -> None:
    """Verify setup_logger creates file handlers and logs messages cleanly."""
    log_file = tmp_path / "test.log"
    logger = setup_logger(name="test_logger", log_level=logging.DEBUG, log_file=log_file)

    assert logger.name == "test_logger"
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) >= 1

    logger.info("Test log entry")

    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "Test log entry" in content


def test_get_logger() -> None:
    """Verify get_logger retrieves instantiated logger instance."""
    logger = get_logger("test_logger")
    assert logger.name == "test_logger"
