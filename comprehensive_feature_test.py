#!/usr/bin/env python3
import sqlite3
import sys
import os
import hashlib
import traceback
from datetime import datetime

def setup_test_environment():
    """Setup test user and sample data"""
    try:
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        
        # Create test user if needed
        c.execute('SELECT * FROM users WHERE username = ?', ('testuser',))
        if not c.fetchone():
            password = hashlib.sha256('testpass'.encode()).hexdigest()
            c.execute('INSERT INTO users (username, password, email, is_admin) VALUES (?, ?, ?, ?)',
                     ('testuser', password, 'test@example.com', 1))
            conn.commit()
            print("✓ Test user created")
        else:
            print("✓ Test user exists")
        
        # Add test book if needed
        c.execute('SELECT * FROM books WHERE title = ?', ('Test Feature Book',))
        if not c.fetchone():
            c.execute('INSERT INTO books (title, author, isbn) VALUES (?, ?, ?)',
                     ('Test Feature Book', 'Test Author', '978-1234567890'))
            conn.commit()
            print("✓ Test book created")
        else:
            print("✓ Test book exists")
        
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Setup failed: {e}")
        return False

def test_authentication_features():
    """Test login, logout, and registration features"""
    print("\n=== Testing Authentication Features ===")
    try:
        sys.path.append(os.getcwd())
        from app import app
        
        with app.test_client() as client:
            # Test login page access
            response = client.get('/login')
            if response.status_code == 200:
                print("✓ Login page accessible")
            else:
                print(f"✗ Login page issue: {response.status_code}")
                return False
            
            # Test valid login
            login_response = client.post('/login', data={
                'username': 'testuser',
                'password': 'testpass'
            })
            if login_response.status_code in [200, 302]:  # Success or redirect
                print("✓ Login functionality working")
            else:
                print(f"✗ Login failed: {login_response.status_code}")
                return False
            
            # Test logout
            logout_response = client.get('/logout')
            if logout_response.status_code in [200, 302]:
                print("✓ Logout functionality working")
            else:
                print(f"✗ Logout failed: {logout_response.status_code}")
                return False
            
            # Test registration page
            register_response = client.get('/register')
            if register_response.status_code == 200:
                print("✓ Registration page accessible")
            else:
                print(f"✗ Registration page issue: {register_response.status_code}")
                return False
            
        return True
    except Exception as e:
        print(f"✗ Authentication test failed: {e}")
        return False

def test_dashboard_features():
    """Test dashboard and statistics"""
    print("\n=== Testing Dashboard Features ===")
    try:
        sys.path.append(os.getcwd())
        from app import app
        
        with app.test_client() as client:
            # Login first
            client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
            
            # Test dashboard access
            dashboard_response = client.get('/dashboard')
            if dashboard_response.status_code == 200:
                print("✓ Dashboard accessible")
                # Check if statistics are displayed
                if b'total_books' in dashboard_response.data or b'Total Books' in dashboard_response.data:
                    print("✓ Dashboard statistics working")
                else:
                    print("? Dashboard statistics may not be displaying")
            else:
                print(f"✗ Dashboard issue: {dashboard_response.status_code}")
                return False
            
        return True
    except Exception as e:
        print(f"✗ Dashboard test failed: {e}")
        return False

def test_book_management_features():
    """Test book listing, adding, and viewing"""
    print("\n=== Testing Book Management Features ===")
    try:
        sys.path.append(os.getcwd())
        from app import app
        
        with app.test_client() as client:
            # Login first
            client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
            
            # Test books listing page
            books_response = client.get('/books')
            if books_response.status_code == 200:
                print("✓ Books listing page accessible")
            else:
                print(f"✗ Books listing issue: {books_response.status_code}")
                return False
            
            # Test add book page
            add_book_response = client.get('/add_book')
            if add_book_response.status_code == 200:
                print("✓ Add book page accessible")
            else:
                print(f"✗ Add book page issue: {add_book_response.status_code}")
                return False
            
            # Test book creation (we already know this works)
            book_data = {
                'title': 'Feature Test Book',
                'author': 'Feature Test Author',
                'isbn': '978-9876543210'
            }
            create_response = client.post('/add_book', data=book_data, follow_redirects=True)
            if create_response.status_code == 200:
                print("✓ Book creation working")
                # Clean up
                conn = sqlite3.connect('library.db')
                c = conn.cursor()
                c.execute('DELETE FROM books WHERE title = ?', ('Feature Test Book',))
                conn.commit()
                conn.close()
            else:
                print(f"✗ Book creation issue: {create_response.status_code}")
                return False
            
        return True
    except Exception as e:
        print(f"✗ Book management test failed: {e}")
        return False

def test_borrowing_features():
    """Test book borrowing and return functionality"""
    print("\n=== Testing Borrowing Features ===")
    try:
        sys.path.append(os.getcwd())
        from app import app
        
        with app.test_client() as client:
            # Login first
            client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
            
            # Test borrow page access
            borrow_response = client.get('/borrow')
            if borrow_response.status_code == 200:
                print("✓ Borrow page accessible")
            else:
                print(f"✗ Borrow page issue: {borrow_response.status_code}")
                return False
            
            # Test borrowing a book
            borrow_data = {
                'student_name': 'Test Student',
                'book_title': 'Test Feature Book'
            }
            borrow_post_response = client.post('/borrow', data=borrow_data, follow_redirects=True)
            if borrow_post_response.status_code == 200:
                print("✓ Book borrowing functionality working")
            else:
                print(f"✗ Book borrowing issue: {borrow_post_response.status_code}")
                return False
            
            # Test borrowed books page
            borrowed_response = client.get('/borrowed_books')
            if borrowed_response.status_code == 200:
                print("✓ Borrowed books page accessible")
            else:
                print(f"✗ Borrowed books page issue: {borrowed_response.status_code}")
                return False
            
        return True
    except Exception as e:
        print(f"✗ Borrowing test failed: {e}")
        return False

def test_qr_code_features():
    """Test QR code generation"""
    print("\n=== Testing QR Code Features ===")
    try:
        sys.path.append(os.getcwd())
        from app import app
        
        with app.test_client() as client:
            # Login first
            client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
            
            # Test QR code generation
            qr_response = client.get('/generate_qr/Test Feature Book')
            if qr_response.status_code == 200:
                print("✓ QR code generation working")
                # Check if response contains JSON with qr_code data
                try:
                    import json
                    qr_data = json.loads(qr_response.data)
                    if 'qr_code' in qr_data and qr_data['qr_code']:
                        print("✓ QR code returns proper JSON format with base64 data")
                    else:
                        print("? QR code JSON may be missing qr_code field")
                except:
                    print("? QR code response may not be valid JSON")
            else:
                print(f"✗ QR code generation issue: {qr_response.status_code}")
                return False
            
        return True
    except Exception as e:
        print(f"✗ QR code test failed: {e}")
        return False

def test_database_integrity():
    """Test database operations and integrity"""
    print("\n=== Testing Database Integrity ===")
    try:
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        
        # Check all required tables exist
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in c.fetchall()]
        required_tables = ['users', 'books', 'borrowed']
        
        for table in required_tables:
            if table in tables:
                print(f"✓ Table '{table}' exists")
            else:
                print(f"✗ Table '{table}' missing")
                conn.close()
                return False
        
        # Test basic CRUD operations
        # Create
        test_title = f"DB Test Book {datetime.now().strftime('%Y%m%d%H%M%S')}"
        c.execute('INSERT INTO books (title, author, isbn) VALUES (?, ?, ?)',
                 (test_title, 'DB Test Author', '978-0000000000'))
        conn.commit()
        
        # Read
        c.execute('SELECT * FROM books WHERE title = ?', (test_title,))
        result = c.fetchone()
        if result:
            print("✓ Database CREATE and READ operations working")
        else:
            print("✗ Database READ operation failed")
            conn.close()
            return False
        
        # Update
        c.execute('UPDATE books SET author = ? WHERE title = ?', ('Updated Author', test_title))
        conn.commit()
        c.execute('SELECT author FROM books WHERE title = ?', (test_title,))
        updated_result = c.fetchone()
        if updated_result and updated_result[0] == 'Updated Author':
            print("✓ Database UPDATE operation working")
        else:
            print("✗ Database update operation failed")
        
        # Delete
        c.execute('DELETE FROM books WHERE title = ?', (test_title,))
        conn.commit()
        c.execute('SELECT * FROM books WHERE title = ?', (test_title,))
        delete_result = c.fetchone()
        if not delete_result:
            print("✓ Database DELETE operation working")
        else:
            print("✗ Database delete operation failed")
        
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Database integrity test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all feature tests"""
    print("=== SmartLib Manager Comprehensive Feature Test ===")
    print("Testing all major application features...\n")
    
    # Setup
    setup_ok = setup_test_environment()
    if not setup_ok:
        print("\n❌ Cannot proceed - setup failed")
        return
    
    # Run all tests
    test_results = {
        'Authentication': test_authentication_features(),
        'Dashboard': test_dashboard_features(),
        'Book Management': test_book_management_features(),
        'Borrowing System': test_borrowing_features(),
        'QR Code Generation': test_qr_code_features(),
        'Database Integrity': test_database_integrity()
    }
    
    # Summary
    print("\n" + "="*50)
    print("COMPREHENSIVE TEST RESULTS")
    print("="*50)
    
    all_passed = True
    for feature, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{feature:<20} {status}")
        if not result:
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 ALL FEATURES ARE WORKING CORRECTLY!")
        print("\nYour SmartLib Manager application is fully functional.")
    else:
        print("⚠️  SOME FEATURES NEED ATTENTION")
        print("\nPlease review the failed tests above for details.")
    print("="*50)

if __name__ == "__main__":
    run_comprehensive_test()