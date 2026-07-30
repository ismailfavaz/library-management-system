# Library Management System

A production-quality Python 3.12+ command-line application built with modular architecture, Object-Oriented Programming (OOP), SQLite storage, fine calculation, reporting/statistics, CSV exports, and JSON database backup/restoration.

---

## Key Features

- **Book Management (CRUD & Search):** Full title cataloguing, available copy tracking, unique ISBN validation (ISBN-10 & ISBN-13 checksums), genre filtering, and case-insensitive keyword search.
- **User Management (CRUD & Search):** Member registration, RFC 5322 email validation, borrowing limits (`max_loans`), and member search.
- **Circulation & Due Dates:** Borrowing and return workflows, loan duration tracking, automatic available stock adjustment, and active loan tracking.
- **Fine Calculation Engine:** Configurable fine strategy (`daily_rate`, `grace_period_days`, `max_fine_cap`) calculating overdue fines upon book returns.
- **Reports & Statistics:** Summary metrics dashboard (total titles, physical copies, active/overdue loans, total fines accrued, genre breakdowns, and top borrowed books).
- **Data Export & Backup:** Export catalog and member data to CSV format, and perform complete database backups/restorations via JSON files.
- **SQLite Database Layer:** Robust database connection manager with context-managed transactions, foreign key enforcement, automatic rollbacks, and schema migrations.
- **Clean CLI Interface:** User-friendly terminal interface with input validation and exception catching.

---

## Project Structure

```text
library-management-system/
│
├── main.py                          # Application CLI entry point
├── requirements.txt                 # Project dependencies (pytest, pytest-cov)
├── README.md                        # Documentation & setup guide
├── .gitignore                       # Git exclusion rules
│
├── src/
│   └── library/
│       ├── __init__.py
│       ├── exceptions.py            # Domain-specific exception hierarchy
│       │
│       ├── models/                  # OOP Data Models
│       │   ├── __init__.py
│       │   └── entities.py          # Book, User, and Loan dataclasses
│       │
│       ├── storage/                 # Persistence Layer
│       │   ├── __init__.py
│       │   ├── db.py                # SQLite connection & transaction manager
│       │   ├── schema.py            # DDL tables & indexes initialization
│       │   ├── book_repository.py   # Book CRUD & search repository
│       │   ├── user_repository.py   # User CRUD & search repository
│       │   └── loan_repository.py   # Loan CRUD repository
│       │
│       ├── services/                # Business Logic Layer
│       │   ├── __init__.py
│       │   ├── book_service.py      # Book domain rules
│       │   ├── user_service.py      # User domain rules
│       │   ├── borrow_service.py    # Loan/Return workflow & overdue engine
│       │   ├── fine_calculator.py   # Strategy pattern fine engine
│       │   ├── report_service.py    # Statistics & metric calculation
│       │   └── backup_service.py    # CSV export & JSON backup/restore
│       │
│       ├── utils/                   # Shared Utilities
│       │   ├── __init__.py
│       │   ├── logger.py            # Centralized logging setup
│       │   └── validators.py        # ISBN, Email, and input validation
│       │
│       └── cli/                     # CLI Presentation Layer
│           ├── __init__.py
│           └── menu.py              # Interactive CLI menu implementation
│
└── tests/                           # Unit Test Suite
    ├── __init__.py
    ├── test_utils.py                # Tests for logger & exceptions
    ├── test_validators.py           # Tests for ISBN & email validators
    ├── test_entities.py             # Tests for domain entity objects
    ├── test_storage.py              # Tests for SQLite database manager
    ├── test_book_repository.py      # Tests for BookRepository
    ├── test_user_repository.py      # Tests for UserRepository
    ├── test_loan_repository.py      # Tests for LoanRepository
    ├── test_services.py             # Tests for Borrow, Book & User services
    └── test_backup.py               # Tests for CSV export & JSON backup
```

---

## Setup & Execution

### Requirements
- **Python 3.12+**

### Installation

```bash
# Clone or navigate to project directory
cd library-management-system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

Launch the application CLI interface:

```bash
python main.py
```

### Running Unit Tests

Run the test suite with `pytest`:

```bash
pytest

# To view test coverage report:
pytest --cov=src
```

---

## Design Principles

- **Modular Architecture:** Layered design separating Presentation (CLI), Business Logic (Services), Data Access (Repositories), and Persistence (SQLite).
- **Single Responsibility Principle (SRP):** Each repository and service class handles a distinct domain capability.
- **Fail-Safe Exception Handling:** Structured custom exception hierarchy (`LibraryError`, `BookNotAvailableError`, `InvalidISBNError`) ensures precise error propagation and user error messages without application crashes.
- **Clean Logging:** Application events, database transactions, and exceptions are logged cleanly to standard output and `logs/library.log`.
