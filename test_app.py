import unittest
import tempfile
import os
import sqlite3
from datetime import datetime, timedelta
import json
import hashlib
from app import app, initialize_database

class LibraryAppTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        
        # Create a temporary database for testing
        self.test_db = tempfile.mktemp() + '.db'
        app.config['DATABASE'] = self.test_db
        
        # Initialize test database directly
        self.initialize_test_database()
        
        # Create test data
        self.create_test_data()
    
    def tearDown(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_db):
            os.unlink(self.test_db)
    
    def initialize_test_database(self):
        """Initialize the test database with required tables"""
        conn = sqlite3.connect(self.test_db)
        c = conn.cursor()
        
        # Create users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                email TEXT,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create books table
        c.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                author TEXT,
                isbn TEXT,
                available INTEGER DEFAULT 1,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create borrowed books table
        c.execute('''
            CREATE TABLE IF NOT EXISTS borrowed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                book_title TEXT NOT NULL,
                borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                return_date TIMESTAMP,
                FOREIGN KEY (book_title) REFERENCES books (title)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_test_data(self):
        """Create test data for testing."""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Create test users
        admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
        user_password = hashlib.sha256('user123'.encode()).hexdigest()
        
        cursor.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                      ('testadmin', admin_password, 1))
        cursor.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                      ('testuser', user_password, 0))
        
        # Create test books
        cursor.execute('''
            INSERT INTO books (title, author, isbn, available)
            VALUES (?, ?, ?, ?)
        ''', ('Test Book 1', 'Test Author 1', '1234567890', 1))
        
        cursor.execute('''
            INSERT INTO books (title, author, isbn, available)
            VALUES (?, ?, ?, ?)
        ''', ('Test Book 2', 'Test Author 2', '0987654321', 1))
        
        # Create test borrowing record
        cursor.execute('''
            INSERT INTO borrowed (student_name, book_title, borrow_date)
            VALUES (?, ?, ?)
        ''', ('John Doe', 'Test Book 1', '2024-01-01'))
        
        conn.commit()
        conn.close()
    
    def get_db_connection(self):
        """Helper method to get database connection"""
        return sqlite3.connect(self.test_db)
    
    def login(self, username, password):
        """Helper method to login a user."""
        return self.app.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)
    
    def logout(self):
        """Helper method to logout a user."""
        return self.app.get('/logout', follow_redirects=True)

class AuthenticationTests(LibraryAppTestCase):
    """Test authentication functionality."""
    
    def test_login_page_loads(self):
        """Test that login page loads correctly."""
        rv = self.app.get('/login')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Login', rv.data)
    
    def test_valid_login(self):
        """Test login with valid credentials."""
        rv = self.login('testadmin', 'admin123')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Dashboard', rv.data)
    
    def test_invalid_login(self):
        """Test login with invalid credentials."""
        rv = self.login('invalid', 'invalid')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Invalid username or password', rv.data)
    
    def test_logout(self):
        """Test user logout."""
        self.login('testadmin', 'admin123')
        rv = self.logout()
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Login', rv.data)
    
    def test_registration(self):
        """Test user registration."""
        rv = self.app.post('/register', data={
            'username': 'newuser',
            'password': 'newpass123',
            'confirm_password': 'newpass123'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Account created successfully', rv.data)
    
    def test_registration_password_mismatch(self):
        """Test registration with password mismatch."""
        rv = self.app.post('/register', data={
            'username': 'newuser',
            'password': 'newpass123',
            'confirm_password': 'different123'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Passwords do not match', rv.data)
    
    def test_registration_existing_user(self):
        """Test registration with existing username."""
        rv = self.app.post('/register', data={
            'username': 'testadmin',
            'password': 'newpass123',
            'confirm_password': 'newpass123'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Username already exists', rv.data)

class DashboardTests(LibraryAppTestCase):
    """Test dashboard functionality."""
    
    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication."""
        rv = self.app.get('/dashboard')
        self.assertEqual(rv.status_code, 302)  # Redirect to login
    
    def test_dashboard_loads_after_login(self):
        """Test that dashboard loads after login."""
        self.login('testadmin', 'admin123')
        rv = self.app.get('/dashboard')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Dashboard', rv.data)
        self.assertIn(b'Total Books', rv.data)
        self.assertIn(b'Available Books', rv.data)
        self.assertIn(b'Borrowed Books', rv.data)

class BookManagementTests(LibraryAppTestCase):
    """Test book management functionality."""
    
    def test_books_page_requires_login(self):
        """Test that books page requires authentication."""
        rv = self.app.get('/books')
        self.assertEqual(rv.status_code, 302)  # Redirect to login
    
    def test_books_page_loads(self):
        """Test that books page loads after login."""
        self.login('testadmin', 'admin123')
        rv = self.app.get('/books')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Books', rv.data)
        self.assertIn(b'Test Book 1', rv.data)
        self.assertIn(b'Test Book 2', rv.data)
    
    def test_add_book_page_loads(self):
        """Test that add book page loads."""
        self.login('testadmin', 'admin123')
        rv = self.app.get('/add_book')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Add New Book', rv.data)
    
    def test_add_book_success(self):
        """Test adding a new book successfully."""
        self.login('testadmin', 'admin123')
        rv = self.app.post('/add_book', data={
            'title': 'New Test Book',
            'author': 'New Test Author',
            'isbn': '1111111111',
            'description': 'New test description',
            'category': 'Test Category',
            'publication_year': '2023'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Book "New Test Book" added successfully', rv.data)
    
    def test_add_book_duplicate_isbn(self):
        """Test adding a book with duplicate ISBN."""
        self.login('testadmin', 'admin123')
        rv = self.app.post('/add_book', data={
            'title': 'Duplicate Book',
            'author': 'Duplicate Author',
            'isbn': '1234567890',  # Same as Test Book 1
            'description': 'Duplicate description',
            'category': 'Test Category',
            'publication_year': '2023'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'A book with ISBN 1234567890 already exists', rv.data)
    
    def test_add_book_missing_fields(self):
        """Test adding a book with missing required fields."""
        self.login('testadmin', 'admin123')
        rv = self.app.post('/add_book', data={
            'title': '',
            'author': 'Test Author',
            'isbn': '2222222222'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Title, author and ISBN are required', rv.data)
    
    def test_books_search(self):
        """Test book search functionality."""
        self.login('testadmin', 'admin123')
        rv = self.app.get('/books?search=Test Book 1')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Test Book 1', rv.data)
        self.assertNotIn(b'Test Book 2', rv.data)
    
    def test_books_filter_available(self):
        """Test filtering available books."""
        self.login('testadmin', 'admin123')
        rv = self.app.get('/books?status=available')
        self.assertEqual(rv.status_code, 200)
        # Test Book 2 should be available (not borrowed)
        self.assertIn(b'Test Book 2', rv.data)

class BorrowingTests(LibraryAppTestCase):
    """Test borrowing functionality."""
    
    def test_borrow_page_requires_login(self):
        """Test that borrow page requires authentication."""
        rv = self.app.get('/borrow')
        self.assertEqual(rv.status_code, 302)  # Redirect to login
    
    def test_borrow_page_loads(self):
        """Test that borrow page loads after login."""
        self.login('testadmin', 'admin123')
        rv = self.app.get('/borrow')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Borrow Book', rv.data)
    
    def test_borrow_book_success(self):
        """Test borrowing a book successfully."""
        self.login('testadmin', 'admin123')
        today = datetime.now().strftime('%Y-%m-%d')
        due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
        
        rv = self.app.post('/borrow', data={
            'student_name': 'Jane Smith',
            'student_id': 'STU002',
            'book_title': 'Test Book 2',
            'borrow_date': today,
            'due_date': due_date,
            'notes': 'Test borrowing'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Book "Test Book 2" has been borrowed by Jane Smith', rv.data)
    
    def test_borrow_missing_fields(self):
        """Test borrowing with missing required fields."""
        self.login('testadmin', 'admin123')
        rv = self.app.post('/borrow', data={
            'student_name': '',
            'book_title': 'Test Book 2'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Student name, book title, borrow date and due date are required', rv.data)
    
    def test_borrowed_books_page_loads(self):
        """Test that borrowed books page loads."""
        self.login('testadmin', 'admin123')
        rv = self.app.get('/borrowed_books')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Borrowed Books', rv.data)
        self.assertIn(b'John Doe', rv.data)  # From test data
    
    def test_return_book_success(self):
        """Test returning a book successfully."""
        self.login('testadmin', 'admin123')
        rv = self.app.get('/return_book/1', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Book "Test Book 1" has been returned', rv.data)
    
    def test_return_nonexistent_book(self):
        """Test returning a non-existent book."""
        self.login('testadmin', 'admin123')
        rv = self.app.get('/return_book/999', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Book not found', rv.data)
    
    def test_borrowed_books_search(self):
        """Test searching borrowed books."""
        self.login('testadmin', 'admin123')
        rv = self.app.get('/borrowed_books?search=John')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'John Doe', rv.data)

class QRCodeTests(LibraryAppTestCase):
    """Test QR code functionality."""
    
    def test_generate_qr_requires_login(self):
        """Test that QR generation requires authentication."""
        rv = self.app.get('/generate_qr/1')
        self.assertEqual(rv.status_code, 302)  # Redirect to login
    
    def test_generate_qr_success(self):
        """Test QR code generation for existing book."""
        self.login('testadmin', 'admin123')
        rv = self.app.get('/generate_qr/1')
        self.assertEqual(rv.status_code, 200)
        # Should contain QR code display elements
        self.assertIn(b'QR Code', rv.data)
    
    def test_generate_qr_nonexistent_book(self):
        """Test QR code generation for non-existent book."""
        self.login('testadmin', 'admin123')
        rv = self.app.get('/generate_qr/999', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Book not found', rv.data)

class DatabaseTests(LibraryAppTestCase):
    """Test database operations."""
    
    def test_database_connection(self):
        """Test database connection."""
        conn = sqlite3.connect(self.test_db)
        self.assertIsNotNone(conn)
        conn.close()
    
    def test_users_table_exists(self):
        """Test that users table exists and has correct structure."""
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        conn.close()
    
    def test_books_table_exists(self):
        """Test that books table exists and has correct structure."""
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='books'")
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        conn.close()
    
    def test_borrowed_table_exists(self):
        """Test that borrowed table exists and has correct structure."""
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='borrowed'")
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        conn.close()

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        AuthenticationTests,
        DashboardTests,
        BookManagementTests,
        BorrowingTests,
        QRCodeTests,
        DatabaseTests
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")