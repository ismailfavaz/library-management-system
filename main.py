"""
Application entry point for the Library Management System.
"""

import sys
from pathlib import Path

# Ensure src/ package directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.library.cli.menu import LibraryCLI


def main() -> None:
    """Initializes and runs the Library Management System CLI application."""
    app = LibraryCLI(db_path="library.db")
    app.run()


if __name__ == "__main__":
    main()
