#!/usr/bin/env python3
import sqlite3
import sys
import os
import hashlib
import traceback
from io import StringIO

def test_with_error_capture():
    """Test book creation and capture any errors"""
    try:
        sys.path.append(os.getcwd())
        from app import app
        
        # Enable debug mode to see errors
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            # Create test user if needed
            conn = sqlite3.connect('library.db')
            c = conn.cursor()
            
            # Check if test user exists
            c.execute('SELECT * FROM users WHERE username = ?', ('testuser',))
            if not c.fetchone():
                password = hashlib.sha256('testpass'.encode()).hexdigest()
                c.execute('INSERT INTO users (username, password, email, is_admin) VALUES (?, ?, ?, ?)',
                         ('testuser', password, 'test@example.com', 1))
                conn.commit()
            conn.close()
            
            # Login
            login_response = client.post('/login', data={
                'username': 'testuser',
                'password': 'testpass'
            })
            
            print(f"Login status: {login_response.status_code}")
            
            # Try to access add_book page
            get_response = client.get('/add_book')
            print(f"GET /add_book status: {get_response.status_code}")
            
            if get_response.status_code != 200:
                print(f"GET response data: {get_response.data.decode()[:500]}")
                return False
            
            # Try to create a book with minimal data
            book_data = {
                'title': 'Simple Test Book',
                'author': 'Test Author',
                'isbn': '123456789'
            }
            
            print("\nAttempting to create book with data:", book_data)
            
            # Capture any errors during POST
            try:
                post_response = client.post('/add_book', data=book_data, follow_redirects=False)
                print(f"POST /add_book status: {post_response.status_code}")
                
                if post_response.status_code == 500:
                    print("500 Error detected!")
                    print(f"Response headers: {dict(post_response.headers)}")
                    print(f"Response data: {post_response.data.decode()[:1000]}")
                elif post_response.status_code == 302:
                    print(f"Redirect to: {post_response.headers.get('Location')}")
                    # Follow redirect to see result
                    follow_response = client.get(post_response.headers.get('Location', '/books'))
                    print(f"Follow-up status: {follow_response.status_code}")
                else:
                    print(f"Unexpected status: {post_response.status_code}")
                    print(f"Response data: {post_response.data.decode()[:500]}")
                
            except Exception as e:
                print(f"Exception during POST: {e}")
                traceback.print_exc()
                return False
            
            # Check if book was created
            conn = sqlite3.connect('library.db')
            c = conn.cursor()
            c.execute('SELECT * FROM books WHERE title = ?', ('Simple Test Book',))
            result = c.fetchone()
            
            if result:
                print(f"✓ Book found in database: {result}")
                # Clean up
                c.execute('DELETE FROM books WHERE title = ?', ('Simple Test Book',))
                conn.commit()
            else:
                print("✗ Book not found in database")
            
            conn.close()
            return True
            
    except Exception as e:
        print(f"Test failed with exception: {e}")
        traceback.print_exc()
        return False

def check_flask_imports():
    """Check if all Flask imports are working"""
    try:
        sys.path.append(os.getcwd())
        print("Testing Flask imports...")
        
        from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
        print("✓ Flask imports successful")
        
        from app import app, login_required
        print("✓ App imports successful")
        
        # Check if templates exist
        template_path = os.path.join(os.getcwd(), 'templates', 'add_book.html')
        if os.path.exists(template_path):
            print("✓ add_book.html template exists")
        else:
            print("✗ add_book.html template missing")
            
        return True
        
    except Exception as e:
        print(f"✗ Import error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Debug Book Creation Error ===")
    print()
    
    print("1. Checking Flask imports...")
    imports_ok = check_flask_imports()
    print()
    
    if imports_ok:
        print("2. Testing book creation with error capture...")
        test_ok = test_with_error_capture()
        print()
        
        if test_ok:
            print("✅ Book creation is working!")
        else:
            print("❌ Book creation has issues - see details above")
    else:
        print("Cannot proceed due to import issues")