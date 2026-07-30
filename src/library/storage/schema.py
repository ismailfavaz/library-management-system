"""
Database schema definition and table creation scripts for SQLite.
"""

from src.library.storage.db import DatabaseManager
from src.library.utils.logger import get_logger

logger = get_logger(__name__)

# SQL Statements for Database Creation

CREATE_BOOKS_TABLE = """
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    isbn TEXT UNIQUE NOT NULL,
    publication_year INTEGER NOT NULL,
    total_copies INTEGER NOT NULL CHECK (total_copies > 0),
    available_copies INTEGER NOT NULL CHECK (available_copies >= 0 AND available_copies <= total_copies),
    genre TEXT DEFAULT 'General'
);
"""

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL,
    role TEXT DEFAULT 'MEMBER',
    password_hash TEXT DEFAULT NULL,
    max_loans INTEGER DEFAULT 5 CHECK (max_loans > 0),
    member_since TEXT NOT NULL
);
"""

CREATE_LOANS_TABLE = """
CREATE TABLE IF NOT EXISTS loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    borrow_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    return_date TEXT DEFAULT NULL,
    fine_amount REAL DEFAULT 0.0 CHECK (fine_amount >= 0.0),
    FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE RESTRICT,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE RESTRICT
);
"""

CREATE_RESERVATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status TEXT DEFAULT 'PENDING',
    reserved_at TEXT NOT NULL,
    FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
"""

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn);",
    "CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);",
    "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
    "CREATE INDEX IF NOT EXISTS idx_loans_user_id ON loans(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_loans_book_id ON loans(book_id);",
    "CREATE INDEX IF NOT EXISTS idx_loans_active ON loans(user_id, return_date);",
    "CREATE INDEX IF NOT EXISTS idx_reservations_queue ON reservations(book_id, status);",
]


def initialize_database(db_manager: DatabaseManager) -> None:
    """Creates database tables and indexes if they do not exist.

    Args:
        db_manager: Configured DatabaseManager instance.
    """
    logger.info("Initializing database schema...")
    with db_manager.session() as conn:
        cursor = conn.cursor()
        cursor.execute(CREATE_BOOKS_TABLE)
        cursor.execute(CREATE_USERS_TABLE)
        cursor.execute(CREATE_LOANS_TABLE)
        cursor.execute(CREATE_RESERVATIONS_TABLE)

        for index_sql in CREATE_INDEXES:
            cursor.execute(index_sql)

    logger.info("Database schema initialized successfully.")
