import unittest
import tempfile
import os
import sqlite3
from datetime import datetime, timedelta
import hashlib
from app import app, initialize_database

class IntegrationTestCase(unittest.TestCase):
    """Integration tests for the complete library management system."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary database for testing
        self.test_db = tempfile.mktemp() + '.db'
        
        # Configure Flask app for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'test-secret-key'
        
        self.app = app.test_client()
        
        # Initialize test database directly
        self.initialize_test_database()
        
        # Create test data
        self.create_test_data()
    
    def tearDown(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_db):
            os.unlink(self.test_db)
    
    def get_db_connection(self):
        """Helper method to get database connection"""
        return sqlite3.connect(self.test_db)
    
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
    
    def login(self, username, password):
        """Helper method to login a user."""
        return self.app.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)
    
    def logout(self):
        """Helper method to logout a user."""
        return self.app.get('/logout', follow_redirects=True)
    
    def test_complete_workflow(self):
        """Test complete library management workflow."""
        # 1. Login
        rv = self.login('testadmin', 'admin123')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Dashboard', rv.data)
        
        # 2. View dashboard
        rv = self.app.get('/dashboard')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Total Books', rv.data)
        
        # 3. Add a new book
        rv = self.app.post('/add_book', data={
            'title': 'Integration Test Book',
            'author': 'Test Author',
            'isbn': '9999999999',
            'description': 'Test description',
            'category': 'Test',
            'publication_year': '2024'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Book "Integration Test Book" added successfully', rv.data)
        
        # 4. View books list
        rv = self.app.get('/books')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Integration Test Book', rv.data)
        
        # 5. Borrow the new book
        today = datetime.now().strftime('%Y-%m-%d')
        due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
        
        rv = self.app.post('/borrow', data={
            'student_name': 'Integration Test Student',
            'student_id': 'INT001',
            'book_title': 'Integration Test Book',
            'borrow_date': today,
            'due_date': due_date,
            'notes': 'Integration test borrowing'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Book "Integration Test Book" has been borrowed', rv.data)
        
        # 6. View borrowed books
        rv = self.app.get('/borrowed_books')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Integration Test Student', rv.data)
        
        # 7. Return the book
        rv = self.app.get('/return_book/3', follow_redirects=True)  # Book ID 3 (newly added)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Book "Integration Test Book" has been returned', rv.data)
        
        # 8. Logout
        rv = self.logout()
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Login', rv.data)
    
    def test_user_registration_and_login(self):
        """Test user registration and subsequent login."""
        # Register new user
        rv = self.app.post('/register', data={
            'username': 'newintegrationuser',
            'password': 'newpass123',
            'confirm_password': 'newpass123'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Account created successfully', rv.data)
        
        # Login with new user
        rv = self.login('newintegrationuser', 'newpass123')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Dashboard', rv.data)
    
    def test_book_search_and_filter(self):
        """Test book search and filtering functionality."""
        self.login('testadmin', 'admin123')
        
        # Search by title
        rv = self.app.get('/books?search=Test Book 1')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Test Book 1', rv.data)
        self.assertNotIn(b'Test Book 2', rv.data)
        
        # Search by author
        rv = self.app.get('/books?search=Test Author 2')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Test Book 2', rv.data)
        self.assertNotIn(b'Test Book 1', rv.data)
        
        # Filter available books
        rv = self.app.get('/books?status=available')
        self.assertEqual(rv.status_code, 200)
        # Should show Test Book 2 (not borrowed)
        self.assertIn(b'Test Book 2', rv.data)
        
        # Filter borrowed books
        rv = self.app.get('/books?status=borrowed')
        self.assertEqual(rv.status_code, 200)
        # Should show Test Book 1 (borrowed in test data)
        self.assertIn(b'Test Book 1', rv.data)
    
    def test_borrowed_books_management(self):
        """Test borrowed books management features."""
        self.login('testadmin', 'admin123')
        
        # View borrowed books
        rv = self.app.get('/borrowed_books')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'John Doe', rv.data)
        
        # Search borrowed books
        rv = self.app.get('/borrowed_books?search=John')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'John Doe', rv.data)
        
        # Filter overdue books (Test Book 1 should be overdue)
        rv = self.app.get('/borrowed_books?status=overdue')
        self.assertEqual(rv.status_code, 200)
        # The test borrowing has due date 2024-01-15, which should be overdue
        self.assertIn(b'John Doe', rv.data)
    
    def test_error_handling(self):
        """Test error handling scenarios."""
        self.login('testadmin', 'admin123')
        
        # Try to add book with duplicate ISBN
        rv = self.app.post('/add_book', data={
            'title': 'Duplicate Book',
            'author': 'Duplicate Author',
            'isbn': '1234567890',  # Same as Test Book 1
            'description': 'Duplicate description',
            'category': 'Test',
            'publication_year': '2023'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'A book with ISBN 1234567890 already exists', rv.data)
        
        # Try to borrow non-existent book
        today = datetime.now().strftime('%Y-%m-%d')
        due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
        
        rv = self.app.post('/borrow', data={
            'student_name': 'Test Student',
            'student_id': 'TEST001',
            'book_title': 'Non-existent Book',
            'borrow_date': today,
            'due_date': due_date
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Book "Non-existent Book" not found', rv.data)
        
        # Try to return non-existent book
        rv = self.app.get('/return_book/999', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Book not found', rv.data)
    
    def test_authentication_protection(self):
        """Test that protected routes require authentication."""
        # Try to access protected routes without login
        protected_routes = [
            '/dashboard',
            '/books',
            '/add_book',
            '/borrow',
            '/borrowed_books',
            '/generate_qr/1'
        ]
        
        for route in protected_routes:
            rv = self.app.get(route)
            self.assertEqual(rv.status_code, 302)  # Should redirect to login
    
    def test_qr_code_generation(self):
        """Test QR code generation functionality."""
        self.login('testadmin', 'admin123')
        
        # Generate QR code for existing book
        rv = self.app.get('/generate_qr/1')
        self.assertEqual(rv.status_code, 200)
        # Should contain QR code display elements
        self.assertIn(b'QR Code', rv.data)
        
        # Try to generate QR for non-existent book
        rv = self.app.get('/generate_qr/999', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Book not found', rv.data)

if __name__ == '__main__':
    unittest.main(verbosity=2)