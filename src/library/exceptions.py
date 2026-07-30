"""
Custom domain exception hierarchy for the Library Management System.
"""


class LibraryError(Exception):
    """Base exception class for all domain-specific errors in the library application."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


# --- Persistence Exceptions ---

class DatabaseError(LibraryError):
    """Raised when a database query or connection operation fails."""
    pass


class RecordNotFoundError(LibraryError):
    """Raised when a requested database record is not found."""
    pass


# --- Entity Exceptions ---

class BookNotFoundError(RecordNotFoundError):
    """Raised when a specified book ID or ISBN does not exist."""

    def __init__(self, identifier: str | int) -> None:
        super().__init__(f"Book with identifier '{identifier}' was not found.")
        self.identifier = identifier


class UserNotFoundError(RecordNotFoundError):
    """Raised when a specified user ID or email does not exist."""

    def __init__(self, identifier: str | int) -> None:
        super().__init__(f"User with identifier '{identifier}' was not found.")
        self.identifier = identifier


# --- Validation Exceptions ---

class ValidationError(LibraryError):
    """Raised when user input or domain validation checks fail."""
    pass


class InvalidISBNError(ValidationError):
    """Raised when a provided ISBN string does not conform to ISBN-10 or ISBN-13 standard."""

    def __init__(self, isbn: str) -> None:
        super().__init__(f"Invalid ISBN format: '{isbn}'. Expected valid ISBN-10 or ISBN-13.")
        self.isbn = isbn


class InvalidEmailError(ValidationError):
    """Raised when an email address format is invalid."""

    def __init__(self, email: str) -> None:
        super().__init__(f"Invalid email address: '{email}'.")
        self.email = email


class DuplicateIsbnError(ValidationError):
    """Raised when attempting to add or update a book with an ISBN that already exists."""

    def __init__(self, isbn: str, existing_title: str | None = None) -> None:
        msg = f"A book with ISBN '{isbn}' already exists"
        if existing_title:
            msg += f": '{existing_title}'"
        super().__init__(msg + ".")
        self.isbn = isbn
        self.existing_title = existing_title


class DuplicateEmailError(ValidationError):
    """Raised when attempting to register or update a user with an email that is already registered."""

    def __init__(self, email: str) -> None:
        super().__init__(f"A user with email '{email}' is already registered.")
        self.email = email



# --- Borrowing / Business Logic Exceptions ---

class BorrowError(LibraryError):
    """Base exception for loan and borrowing rule violations."""
    pass


class BookNotAvailableError(BorrowError):
    """Raised when attempting to borrow a book that is currently checked out."""

    def __init__(self, book_title: str) -> None:
        super().__init__(f"Book '{book_title}' is currently checked out and unavailable.")
        self.book_title = book_title


class MaxLoansExceededError(BorrowError):
    """Raised when a user has reached their maximum borrowing limit."""

    def __init__(self, user_name: str, max_limit: int) -> None:
        super().__init__(f"User '{user_name}' has reached the maximum loan limit of {max_limit} books.")
        self.max_limit = max_limit


class BookNotBorrowedByUserError(BorrowError):
    """Raised when trying to return a book that was not borrowed by the specified user."""

    def __init__(self, book_id: int, user_id: int) -> None:
        super().__init__(f"Book ID {book_id} is not currently borrowed by User ID {user_id}.")
        self.book_id = book_id
        self.user_id = user_id
