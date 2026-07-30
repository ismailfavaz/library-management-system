"""
Interactive Command Line Interface (CLI) menu system.
"""

from pathlib import Path
import sys

from src.library.exceptions import LibraryError
from src.library.services.backup_service import BackupService
from src.library.services.book_service import BookService
from src.library.services.borrow_service import BorrowService
from src.library.services.report_service import ReportService
from src.library.services.user_service import UserService
from src.library.storage.book_repository import BookRepository
from src.library.storage.db import DatabaseManager
from src.library.storage.loan_repository import LoanRepository
from src.library.storage.schema import initialize_database
from src.library.storage.user_repository import UserRepository
from src.library.utils.logger import setup_logger

logger = setup_logger(name="library_cli", log_file="logs/library.log")


class LibraryCLI:
    """Main CLI Menu Controller."""

    def __init__(self, db_path: str = "library.db") -> None:
        self.db_manager = DatabaseManager(db_path)
        initialize_database(self.db_manager)

        self.book_repo = BookRepository(self.db_manager)
        self.user_repo = UserRepository(self.db_manager)
        self.loan_repo = LoanRepository(self.db_manager)

        self.book_service = BookService(self.book_repo)
        self.user_service = UserService(self.user_repo)
        self.borrow_service = BorrowService(self.book_repo, self.user_repo, self.loan_repo)
        self.report_service = ReportService(self.book_repo, self.user_repo, self.loan_repo)
        self.backup_service = BackupService(self.book_repo, self.user_repo, self.loan_repo)

    def run(self) -> None:
        """Starts the CLI main loop."""
        print("\n=======================================================")
        print("     WELCOME TO LIBRARY MANAGEMENT SYSTEM v0.1.0       ")
        print("=======================================================")

        while True:
            self._print_main_menu()
            choice = input("Enter option (0-6): ").strip()

            if choice == "1":
                self._book_menu()
            elif choice == "2":
                self._user_menu()
            elif choice == "3":
                self._circulation_menu()
            elif choice == "4":
                self._report_menu()
            elif choice == "5":
                self._backup_menu()
            elif choice == "6":
                self._seed_sample_data()
            elif choice == "0":
                print("\nThank you for using Library Management System. Goodbye!")
                sys.exit(0)
            else:
                print("\n[!] Invalid selection. Please enter a number from 0 to 6.")

    def _print_main_menu(self) -> None:
        print("\n--- MAIN MENU ---")
        print("1. Book Management (CRUD, Search)")
        print("2. User Management (CRUD, Search)")
        print("3. Borrow & Return Operations")
        print("4. Reports & Statistics")
        print("5. Backup & Export (CSV, JSON)")
        print("6. Seed Sample Data")
        print("0. Exit")

    # --- BOOK MANAGEMENT ---

    def _book_menu(self) -> None:
        while True:
            print("\n--- BOOK MANAGEMENT ---")
            print("1. Add New Book")
            print("2. View All Books")
            print("3. Search Books")
            print("4. Update Book")
            print("5. Delete Book")
            print("0. Back to Main Menu")

            choice = input("Option: ").strip()
            if choice == "1":
                self._add_book()
            elif choice == "2":
                self._list_books()
            elif choice == "3":
                self._search_books()
            elif choice == "4":
                self._update_book()
            elif choice == "5":
                self._delete_book()
            elif choice == "0":
                break

    def _add_book(self) -> None:
        print("\n[Add New Book]")
        try:
            title = input("Title: ")
            author = input("Author: ")
            isbn = input("ISBN: ")
            year = int(input("Publication Year: "))
            copies = int(input("Total Copies: "))
            genre = input("Genre [Default: General]: ").strip() or "General"

            book = self.book_service.add_book(title, author, isbn, year, copies, genre)
            print(f"\n[+] Success: Book added with ID {book.id}")
        except LibraryError as err:
            print(f"\n[!] Error: {err}")
        except ValueError as err:
            print(f"\n[!] Input Error: {err}")

    def _list_books(self) -> None:
        books = self.book_service.get_all_books()
        print(f"\n--- CATALOG ({len(books)} titles) ---")
        if not books:
            print("No books registered yet.")
            return

        fmt = "{:<5} | {:<30} | {:<20} | {:<14} | {:<6} | {:<10}"
        print(fmt.format("ID", "Title", "Author", "ISBN", "Avail", "Genre"))
        print("-" * 95)
        for b in books:
            avail_str = f"{b.available_copies}/{b.total_copies}"
            print(fmt.format(b.id or 0, b.title[:30], b.author[:20], b.isbn, avail_str, b.genre[:10]))

    def _search_books(self) -> None:
        query = input("\nEnter title, author, ISBN, or genre keyword: ").strip()
        if not query:
            return
        books = self.book_service.search_books(query)
        print(f"\n--- SEARCH RESULTS ({len(books)} matches) ---")
        fmt = "{:<5} | {:<30} | {:<20} | {:<14} | {:<6} | {:<10}"
        print(fmt.format("ID", "Title", "Author", "ISBN", "Avail", "Genre"))
        print("-" * 95)
        for b in books:
            avail_str = f"{b.available_copies}/{b.total_copies}"
            print(fmt.format(b.id or 0, b.title[:30], b.author[:20], b.isbn, avail_str, b.genre[:10]))

    def _update_book(self) -> None:
        try:
            book_id = int(input("\nEnter Book ID to update: "))
            book = self.book_service.get_book_by_id(book_id)
            print(f"Updating: '{book.title}' by {book.author}")

            title = input(f"New Title [{book.title}]: ").strip() or None
            author = input(f"New Author [{book.author}]: ").strip() or None
            genre = input(f"New Genre [{book.genre}]: ").strip() or None
            year_in = input(f"New Year [{book.publication_year}]: ").strip()
            year = int(year_in) if year_in else None
            copies_in = input(f"New Total Copies [{book.total_copies}]: ").strip()
            copies = int(copies_in) if copies_in else None

            self.book_service.update_book(book_id, title, author, year, copies, genre)
            print(f"\n[+] Success: Updated Book ID {book_id}")
        except LibraryError as err:
            print(f"\n[!] Error: {err}")
        except ValueError as err:
            print(f"\n[!] Input Error: {err}")

    def _delete_book(self) -> None:
        try:
            book_id = int(input("\nEnter Book ID to delete: "))
            self.book_service.delete_book(book_id)
            print(f"\n[+] Success: Deleted Book ID {book_id}")
        except LibraryError as err:
            print(f"\n[!] Error: {err}")

    # --- USER MANAGEMENT ---

    def _user_menu(self) -> None:
        while True:
            print("\n--- USER MANAGEMENT ---")
            print("1. Register New User")
            print("2. View All Members")
            print("3. Search Users")
            print("4. Update User Profile")
            print("5. Delete User")
            print("0. Back to Main Menu")

            choice = input("Option: ").strip()
            if choice == "1":
                self._register_user()
            elif choice == "2":
                self._list_users()
            elif choice == "3":
                self._search_users()
            elif choice == "4":
                self._update_user()
            elif choice == "5":
                self._delete_user()
            elif choice == "0":
                break

    def _register_user(self) -> None:
        print("\n[Register New User]")
        try:
            name = input("Full Name: ")
            email = input("Email: ")
            phone = input("Phone: ")
            max_loans_in = input("Max Loans [Default 5]: ").strip()
            max_loans = int(max_loans_in) if max_loans_in else 5

            user = self.user_service.register_user(name, email, phone, max_loans)
            print(f"\n[+] Success: Registered user '{user.name}' with ID {user.id}")
        except LibraryError as err:
            print(f"\n[!] Error: {err}")
        except ValueError as err:
            print(f"\n[!] Input Error: {err}")

    def _list_users(self) -> None:
        users = self.user_service.get_all_users()
        print(f"\n--- REGISTERED MEMBERS ({len(users)}) ---")
        if not users:
            print("No members registered.")
            return

        fmt = "{:<5} | {:<25} | {:<30} | {:<15} | {:<10}"
        print(fmt.format("ID", "Name", "Email", "Phone", "Max Loans"))
        print("-" * 90)
        for u in users:
            print(fmt.format(u.id or 0, u.name[:25], u.email[:30], u.phone[:15], u.max_loans))

    def _search_users(self) -> None:
        query = input("\nEnter name, email, or phone: ").strip()
        if not query:
            return
        users = self.user_service.search_users(query)
        print(f"\n--- SEARCH RESULTS ({len(users)} matches) ---")
        fmt = "{:<5} | {:<25} | {:<30} | {:<15} | {:<10}"
        print(fmt.format("ID", "Name", "Email", "Phone", "Max Loans"))
        print("-" * 90)
        for u in users:
            print(fmt.format(u.id or 0, u.name[:25], u.email[:30], u.phone[:15], u.max_loans))

    def _update_user(self) -> None:
        try:
            user_id = int(input("\nEnter User ID to update: "))
            user = self.user_service.get_user_by_id(user_id)
            print(f"Updating Member: '{user.name}' ({user.email})")

            name = input(f"New Name [{user.name}]: ").strip() or None
            email = input(f"New Email [{user.email}]: ").strip() or None
            phone = input(f"New Phone [{user.phone}]: ").strip() or None
            loans_in = input(f"New Max Loans [{user.max_loans}]: ").strip()
            max_loans = int(loans_in) if loans_in else None

            self.user_service.update_user(user_id, name, email, phone, max_loans)
            print(f"\n[+] Success: Updated User ID {user_id}")
        except LibraryError as err:
            print(f"\n[!] Error: {err}")
        except ValueError as err:
            print(f"\n[!] Input Error: {err}")

    def _delete_user(self) -> None:
        try:
            user_id = int(input("\nEnter User ID to delete: "))
            self.user_service.delete_user(user_id)
            print(f"\n[+] Success: Deleted User ID {user_id}")
        except LibraryError as err:
            print(f"\n[!] Error: {err}")

    # --- CIRCULATION MANAGEMENT ---

    def _circulation_menu(self) -> None:
        while True:
            print("\n--- BORROW & RETURN OPERATIONS ---")
            print("1. Borrow Book")
            print("2. Return Book")
            print("3. View Active Loans")
            print("4. View Overdue Loans & Accrued Fines")
            print("5. Renew Active Loan")
            print("0. Back to Main Menu")

            choice = input("Option: ").strip()
            if choice == "1":
                self._borrow_book()
            elif choice == "2":
                self._return_book()
            elif choice == "3":
                self._list_active_loans()
            elif choice == "4":
                self._list_overdue_loans()
            elif choice == "5":
                self._renew_loan()
            elif choice == "0":
                break

    def _renew_loan(self) -> None:
        print("\n[Renew Active Loan]")
        try:
            user_id = int(input("User ID: "))
            book_id = int(input("Book ID: "))
            days_in = input("Extension Days [Default 14]: ").strip()
            extension_days = int(days_in) if days_in else 14

            loan = self.borrow_service.renew_loan(user_id, book_id, extension_days)
            print(f"\n[+] Success! Loan ID {loan.id} renewed. New due date: {loan.due_date}")
        except LibraryError as err:
            print(f"\n[!] Error: {err}")
        except ValueError as err:
            print(f"\n[!] Input Error: {err}")


    def _borrow_book(self) -> None:
        print("\n[Borrow Book]")
        try:
            user_id = int(input("User ID: "))
            book_id = int(input("Book ID: "))
            duration_in = input("Loan Duration in Days [Default 14]: ").strip()
            duration = int(duration_in) if duration_in else 14

            loan = self.borrow_service.borrow_book(user_id, book_id, duration)
            print(f"\n[+] Success! Loan created (ID: {loan.id}). Due date: {loan.due_date}")
        except LibraryError as err:
            print(f"\n[!] Error: {err}")
        except ValueError as err:
            print(f"\n[!] Input Error: {err}")

    def _return_book(self) -> None:
        print("\n[Return Book]")
        try:
            user_id = int(input("User ID: "))
            book_id = int(input("Book ID: "))
            ret_date = input("Return Date (YYYY-MM-DD) [Default Today]: ").strip() or None

            loan, fine = self.borrow_service.return_book(user_id, book_id, ret_date)
            print(f"\n[+] Success: Book ID {book_id} returned.")
            if fine > 0:
                print(f"[!] Accrued Overdue Fine: ${fine:.2f}")
            else:
                print("[+] Returned on time with $0 fine.")
        except LibraryError as err:
            print(f"\n[!] Error: {err}")
        except ValueError as err:
            print(f"\n[!] Input Error: {err}")

    def _list_active_loans(self) -> None:
        loans = self.borrow_service.loan_repo.get_all_active_loans()
        print(f"\n--- ACTIVE LOANS ({len(loans)}) ---")
        if not loans:
            print("No active loans.")
            return

        fmt = "{:<5} | {:<8} | {:<8} | {:<12} | {:<12} | {:<10}"
        print(fmt.format("ID", "User ID", "Book ID", "Borrow Date", "Due Date", "Status"))
        print("-" * 65)
        for l in loans:
            overdue = l.calculate_overdue_days()
            status = f"OVERDUE ({overdue}d)" if overdue > 0 else "Active"
            print(fmt.format(l.id or 0, l.user_id, l.book_id, l.borrow_date, l.due_date, status))

    def _list_overdue_loans(self) -> None:
        overdues = self.borrow_service.get_overdue_loans()
        print(f"\n--- OVERDUE LOANS & FINES ({len(overdues)}) ---")
        if not overdues:
            print("No overdue loans!")
            return

        fmt = "{:<5} | {:<8} | {:<8} | {:<12} | {:<8} | {:<10}"
        print(fmt.format("ID", "User ID", "Book ID", "Due Date", "Overdue", "Fine ($)"))
        print("-" * 60)
        for loan, days, fine in overdues:
            print(fmt.format(loan.id or 0, loan.user_id, loan.book_id, loan.due_date, f"{days} days", f"${fine:.2f}"))

    # --- REPORTS & STATISTICS ---

    def _report_menu(self) -> None:
        print("\n--- LIBRARY SUMMARY REPORT ---")
        stats = self.report_service.get_summary_statistics()

        print(f"Total Book Titles:      {stats['total_titles']}")
        print(f"Total Physical Copies:  {stats['total_copies']}")
        print(f"Available Copies:       {stats['available_copies']}")
        print(f"Currently Borrowed:     {stats['borrowed_copies']}")
        print(f"Registered Members:     {stats['total_users']}")
        print(f"Active Loans:           {stats['active_loans']}")
        print(f"Overdue Loans:          {stats['overdue_loans']}")
        print(f"Total Fines Accrued:    ${stats['total_fines_collected']:.2f}")

        print("\nGenre Breakdown:")
        for genre, count in stats['genre_distribution'].items():
            print(f"  - {genre}: {count} titles")

        top_books = self.report_service.get_most_borrowed_books(limit=3)
        if top_books:
            print("\nTop Borrowed Books:")
            for b in top_books:
                print(f"  - '{b['title']}' by {b['author']} ({b['borrow_count']} borrows)")

    # --- BACKUP & EXPORT ---

    def _backup_menu(self) -> None:
        while True:
            print("\n--- BACKUP & EXPORT ---")
            print("1. Export Books to CSV")
            print("2. Export Users to CSV")
            print("3. Export Loans to CSV")
            print("4. Backup Database to JSON")
            print("5. Restore Database from JSON Backup")
            print("0. Back to Main Menu")

            choice = input("Option: ").strip()
            if choice == "1":
                p = self.backup_service.export_books_to_csv("exports/books.csv")
                print(f"\n[+] Exported books to {p.resolve()}")
            elif choice == "2":
                p = self.backup_service.export_users_to_csv("exports/users.csv")
                print(f"\n[+] Exported users to {p.resolve()}")
            elif choice == "3":
                p = self.backup_service.export_loans_to_csv("exports/loans.csv")
                print(f"\n[+] Exported loans to {p.resolve()}")
            elif choice == "4":
                p = self.backup_service.backup_to_json("backups/library_backup.json")
                print(f"\n[+] Backup created at {p.resolve()}")
            elif choice == "5":
                file_in = input("JSON Backup File Path [backups/library_backup.json]: ").strip() or "backups/library_backup.json"
                try:
                    res = self.backup_service.restore_from_json(file_in)
                    print(f"\n[+] Restored: {res['imported_books']} books, {res['imported_users']} users, {res['imported_loans']} loans.")
                except LibraryError as err:
                    print(f"\n[!] Error: {err}")
            elif choice == "0":
                break

    # --- SEED DEMO DATA ---

    def _seed_sample_data(self) -> None:
        print("\nSeeding sample books and members...")
        try:
            self.book_service.add_book("Clean Code", "Robert C. Martin", "978-0-13-235088-4", 2008, 3, "Software")
            self.book_service.add_book("Design Patterns", "Erich Gamma et al.", "0-201-63361-2", 1994, 2, "Architecture")
            self.book_service.add_book("The Pragmatic Programmer", "Andy Hunt", "0-201-61622-X", 1999, 4, "Software")

            self.user_service.register_user("Alice Johnson", "alice@example.com", "555-0101")
            self.user_service.register_user("Bob Smith", "bob@example.com", "555-0102")

            print("[+] Sample data seeded successfully!")
        except LibraryError as err:
            print(f"[!] Seeding info: {err}")
