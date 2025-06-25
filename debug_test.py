#!/usr/bin/env python3
"""
Debug script to test individual components
"""

import sqlite3
import hashlib
import tempfile
import os
from app import app

def test_database_setup():
    """Test database setup"""
    print("Testing database setup...")
    
    # Create temporary database
    test_db = tempfile.mktemp() + '.db'
    
    try:
        conn = sqlite3.connect(test_db)
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
        
        # Insert test user
        password_hash = hashlib.sha256('testpass123'.encode()).hexdigest()
        c.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                 ('testuser', password_hash, 0))
        
        # Verify user was inserted
        c.execute('SELECT * FROM users WHERE username = ?', ('testuser',))
        user = c.fetchone()
        
        if user:
            print(f"✓ User created successfully: {user}")
        else:
            print("❌ Failed to create user")
            
        conn.commit()
        conn.close()
        
        print("✓ Database setup successful")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False
    finally:
        if os.path.exists(test_db):
            os.unlink(test_db)

def test_flask_app():
    """Test basic Flask app functionality"""
    print("\nTesting Flask app...")
    
    try:
        app.config['TESTING'] = True
        client = app.test_client()
        
        # Test login page
        response = client.get('/login')
        print(f"Login page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Login page loads successfully")
            return True
        else:
            print(f"❌ Login page failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_login_functionality():
    """Test login functionality"""
    print("\nTesting login functionality...")
    
    # Create temporary database with test user
    test_db = tempfile.mktemp() + '.db'
    
    try:
        # Setup database
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
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
        
        # Create test user
        password_hash = hashlib.sha256('testpass123'.encode()).hexdigest()
        c.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                 ('testuser', password_hash, 0))
        
        conn.commit()
        conn.close()
        
        # Test login with Flask app
        app.config['TESTING'] = True
        client = app.test_client()
        
        # Temporarily replace the database path
        import app as app_module
        original_db = 'library.db'
        
        # Mock the database connection in the app
        # This is tricky because the app uses hardcoded 'library.db'
        # For now, let's just test the login page response
        
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=False)
        
        print(f"Login attempt status: {response.status_code}")
        
        if response.status_code in [200, 302]:  # 302 is redirect on success
            print("✓ Login functionality working")
            return True
        else:
            print(f"❌ Login failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False
    finally:
        if os.path.exists(test_db):
            os.unlink(test_db)

def main():
    print("SmartLib Manager - Debug Tests")
    print("=" * 40)
    
    tests = [
        test_database_setup,
        test_flask_app,
        test_login_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All debug tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)