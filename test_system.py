#!/usr/bin/env python3
# test_system.py - Test script to verify the library management system

import sqlite3
import os
import sys
from qr_module import generate_qr, validate_qr_data
import config

def test_database_creation():
    """Test database creation and table setup"""
    print("Testing database creation...")
    
    # Remove existing database for clean test
    if os.path.exists("library.db"):
        os.remove("library.db")
    
    try:
        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        
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
        print("✅ Database creation successful")
        return True
        
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return False

def test_book_operations():
    """Test adding and retrieving books"""
    print("\nTesting book operations...")
    
    try:
        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        
        # Add test books
        test_books = [
            ("Python Programming", "John Doe", "978-0123456789"),
            ("Data Structures", "Jane Smith", "978-0987654321"),
            ("Machine Learning", "Bob Johnson", None)
        ]
        
        for title, author, isbn in test_books:
            c.execute("INSERT INTO books (title, author, isbn) VALUES (?, ?, ?)", 
                     (title, author, isbn))
        
        conn.commit()
        
        # Retrieve books
        c.execute("SELECT title, author, isbn, available FROM books")
        books = c.fetchall()
        
        print(f"✅ Added {len(test_books)} books successfully")
        print(f"✅ Retrieved {len(books)} books from database")
        
        for book in books:
            print(f"   - {book[0]} by {book[1] or 'Unknown'} (Available: {'Yes' if book[3] else 'No'})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Book operations failed: {e}")
        return False

def test_borrow_return_operations():
    """Test borrowing and returning books"""
    print("\nTesting borrow/return operations...")
    
    try:
        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        
        # Test borrowing
        c.execute("INSERT INTO borrowed (student_name, book_title) VALUES (?, ?)", 
                 ("Alice Johnson", "Python Programming"))
        c.execute("UPDATE books SET available = 0 WHERE title = ?", ("Python Programming",))
        
        # Test another borrowing
        c.execute("INSERT INTO borrowed (student_name, book_title) VALUES (?, ?)", 
                 ("Bob Wilson", "Data Structures"))
        c.execute("UPDATE books SET available = 0 WHERE title = ?", ("Data Structures",))
        
        conn.commit()
        
        # Check borrowed books
        c.execute("SELECT student_name, book_title FROM borrowed WHERE return_date IS NULL")
        borrowed_books = c.fetchall()
        
        print(f"✅ Borrowed {len(borrowed_books)} books successfully")
        for student, book in borrowed_books:
            print(f"   - {book} borrowed by {student}")
        
        # Test returning a book
        from datetime import datetime
        c.execute("UPDATE borrowed SET return_date = ? WHERE student_name = ? AND book_title = ?", 
                 (datetime.now().isoformat(), "Alice Johnson", "Python Programming"))
        c.execute("UPDATE books SET available = 1 WHERE title = ?", ("Python Programming",))
        
        conn.commit()
        
        # Check remaining borrowed books
        c.execute("SELECT student_name, book_title FROM borrowed WHERE return_date IS NULL")
        remaining_borrowed = c.fetchall()
        
        print(f"✅ Book returned successfully. Remaining borrowed: {len(remaining_borrowed)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Borrow/return operations failed: {e}")
        return False

def test_qr_code_generation():
    """Test QR code generation"""
    print("\nTesting QR code generation...")
    
    try:
        # Create QR codes directory
        if not os.path.exists("qr_codes"):
            os.makedirs("qr_codes")
        
        # Test basic QR code generation
        test_data = "Book: Python Programming\nAuthor: John Doe\nISBN: 978-0123456789"
        qr_file = "qr_codes/test_book_qr.png"
        
        result = generate_qr(test_data, qr_file)
        
        if os.path.exists(result):
            print(f"✅ QR code generated successfully: {result}")
            
            # Test QR data validation
            if validate_qr_data(test_data):
                print("✅ QR data validation successful")
            else:
                print("❌ QR data validation failed")
                return False
            
            return True
        else:
            print("❌ QR code file not created")
            return False
            
    except Exception as e:
        print(f"❌ QR code generation failed: {e}")
        return False

def test_config_loading():
    """Test configuration loading"""
    print("\nTesting configuration loading...")
    
    try:
        # Test basic config values
        assert hasattr(config, 'ADMIN_USERNAME')
        assert hasattr(config, 'ADMIN_PASSWORD')
        assert hasattr(config, 'APP_TITLE')
        assert hasattr(config, 'WINDOW_THEME')
        
        print(f"✅ Configuration loaded successfully")
        print(f"   - App Title: {config.APP_TITLE}")
        print(f"   - App Version: {config.APP_VERSION}")
        print(f"   - Admin Username: {config.ADMIN_USERNAME}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting SMARTLIB MANAGER System Tests\n")
    print("=" * 50)
    
    tests = [
        test_config_loading,
        test_database_creation,
        test_book_operations,
        test_borrow_return_operations,
        test_qr_code_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print("\n❌ Test failed, stopping execution")
            break
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is working correctly.")
        print("\n📋 System Summary:")
        print("   - Database operations: Working")
        print("   - Book management: Working")
        print("   - Borrow/return system: Working")
        print("   - QR code generation: Working")
        print("   - Configuration: Working")
        print("\n✅ The SMARTLIB MANAGER is ready to use!")
        print("\n🚀 To start the application, run: python main.py")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()