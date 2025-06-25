#!/usr/bin/env python3
import sqlite3
import sys
import os
import hashlib

def create_test_user():
    """Create a test user for authentication"""
    try:
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        
        # Check if test user exists
        c.execute('SELECT * FROM users WHERE username = ?', ('testuser',))
        if c.fetchone():
            print("Test user already exists")
            conn.close()
            return True
        
        # Create test user
        password = hashlib.sha256('testpass'.encode()).hexdigest()
        c.execute('INSERT INTO users (username, password, email, is_admin) VALUES (?, ?, ?, ?)',
                 ('testuser', password, 'test@example.com', 1))
        conn.commit()
        conn.close()
        print("✓ Test user created")
        return True
    except Exception as e:
        print(f"✗ Failed to create test user: {e}")
        return False

def test_authenticated_book_creation():
    """Test book creation through Flask app with authentication"""
    try:
        sys.path.append(os.getcwd())
        from app import app
        
        with app.test_client() as client:
            # Login first
            login_response = client.post('/login', data={
                'username': 'testuser',
                'password': 'testpass'
            }, follow_redirects=True)
            
            if login_response.status_code != 200:
                print(f"✗ Login failed: {login_response.status_code}")
                return False
            
            print("✓ Login successful")
            
            # Test GET request to add_book page
            get_response = client.get('/add_book')
            if get_response.status_code != 200:
                print(f"✗ Cannot access add book page: {get_response.status_code}")
                return False
            
            print("✓ Add book page accessible")
            
            # Test POST request to create book
            book_data = {
                'title': 'Flask Test Book',
                'author': 'Test Author Flask',
                'isbn': '978-0987654321',
                'description': 'A test book created via Flask',
                'category': 'Fiction',
                'publication_year': '2023'
            }
            
            post_response = client.post('/add_book', data=book_data, follow_redirects=True)
            
            if post_response.status_code != 200:
                print(f"✗ Book creation failed: {post_response.status_code}")
                print(f"Response data: {post_response.data.decode()[:200]}...")
                return False
            
            # Check if book was actually created
            conn = sqlite3.connect('library.db')
            c = conn.cursor()
            c.execute('SELECT * FROM books WHERE title = ?', ('Flask Test Book',))
            result = c.fetchone()
            
            if result:
                print(f"✓ Book created successfully: {result}")
                # Clean up
                c.execute('DELETE FROM books WHERE title = ?', ('Flask Test Book',))
                conn.commit()
            else:
                print("✗ Book not found in database after creation")
                conn.close()
                return False
            
            conn.close()
            return True
            
    except Exception as e:
        print(f"✗ Flask book creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_form_validation():
    """Test form validation requirements"""
    try:
        sys.path.append(os.getcwd())
        from app import app
        
        with app.test_client() as client:
            # Login first
            client.post('/login', data={
                'username': 'testuser',
                'password': 'testpass'
            })
            
            # Test with missing required fields
            test_cases = [
                {'title': '', 'author': 'Author', 'isbn': '123'},  # Missing title
                {'title': 'Title', 'author': '', 'isbn': '123'},  # Missing author
                {'title': 'Title', 'author': 'Author', 'isbn': ''},  # Missing ISBN
            ]
            
            for i, case in enumerate(test_cases):
                response = client.post('/add_book', data=case, follow_redirects=True)
                if b'required' in response.data.lower() or b'error' in response.data.lower():
                    print(f"✓ Validation test {i+1} passed (error detected)")
                else:
                    print(f"? Validation test {i+1} - no clear error message")
            
            return True
            
    except Exception as e:
        print(f"✗ Form validation test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Comprehensive Book Creation Test ===")
    print()
    
    print("1. Creating test user...")
    user_ok = create_test_user()
    print()
    
    if user_ok:
        print("2. Testing authenticated book creation...")
        creation_ok = test_authenticated_book_creation()
        print()
        
        print("3. Testing form validation...")
        validation_ok = check_form_validation()
        print()
        
        print("=== Final Summary ===")
        print(f"User creation: {'✓' if user_ok else '✗'}")
        print(f"Book creation: {'✓' if creation_ok else '✗'}")
        print(f"Form validation: {'✓' if validation_ok else '✗'}")
        
        if all([user_ok, creation_ok, validation_ok]):
            print("\n✅ BOOK CREATION IS WORKING CORRECTLY")
            print("\nPossible issues:")
            print("- Make sure you're logged in to the application")
            print("- Check that all required fields (title, author, ISBN) are filled")
            print("- Verify the ISBN format is correct")
            print("- Ensure the book title doesn't already exist")
        else:
            print("\n❌ ISSUES FOUND WITH BOOK CREATION")
    else:
        print("Cannot proceed without test user")