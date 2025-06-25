#!/usr/bin/env python3
import sqlite3
import sys
import os

def check_database_schema():
    """Check the current database schema"""
    try:
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        
        # Check if tables exist
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        print("Database tables:", [t[0] for t in tables])
        
        # Check books table schema
        c.execute("PRAGMA table_info(books)")
        columns = c.fetchall()
        print("Books table columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False

def test_book_insertion():
    """Test inserting a book directly into the database"""
    try:
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        
        # Try to insert a test book
        test_title = "Test Book Creation"
        test_author = "Test Author"
        test_isbn = "978-0123456789"
        
        c.execute('INSERT INTO books (title, author, isbn) VALUES (?, ?, ?)',
                 (test_title, test_author, test_isbn))
        conn.commit()
        
        # Verify insertion
        c.execute('SELECT * FROM books WHERE title = ?', (test_title,))
        result = c.fetchone()
        
        if result:
            print(f"✓ Book insertion successful: {result}")
            # Clean up test data
            c.execute('DELETE FROM books WHERE title = ?', (test_title,))
            conn.commit()
        else:
            print("✗ Book insertion failed - no result found")
        
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Book insertion failed: {e}")
        return False

def check_flask_app():
    """Check if Flask app can be imported and routes exist"""
    try:
        sys.path.append(os.getcwd())
        from app import app
        
        with app.test_client() as client:
            # Test if add_book route exists
            response = client.get('/add_book')
            print(f"Add book route status: {response.status_code}")
            
            if response.status_code == 302:  # Redirect (likely to login)
                print("Route exists but requires authentication")
                return True
            elif response.status_code == 200:
                print("Route accessible")
                return True
            else:
                print(f"Route issue: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"Flask app error: {e}")
        return False

if __name__ == "__main__":
    print("=== Book Creation Diagnostic ===")
    print()
    
    print("1. Checking database schema...")
    db_ok = check_database_schema()
    print()
    
    print("2. Testing direct book insertion...")
    insert_ok = test_book_insertion()
    print()
    
    print("3. Checking Flask app routes...")
    flask_ok = check_flask_app()
    print()
    
    print("=== Summary ===")
    print(f"Database: {'✓' if db_ok else '✗'}")
    print(f"Direct insertion: {'✓' if insert_ok else '✗'}")
    print(f"Flask routes: {'✓' if flask_ok else '✗'}")
    
    if all([db_ok, insert_ok, flask_ok]):
        print("\n✓ All checks passed - book creation should work")
    else:
        print("\n✗ Issues found - see details above")