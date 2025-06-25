from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import sqlite3
import os
from datetime import datetime
import hashlib
from functools import wraps
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change this in production

# Database initialization
def initialize_database():
    """Initialize the database with required tables"""
    conn = sqlite3.connect("library.db")
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
    
    # Create default admin user if not exists
    admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
    c.execute('''
        INSERT OR IGNORE INTO users (username, password, is_admin) 
        VALUES (?, ?, 1)
    ''', ('admin', admin_password))
    
    conn.commit()
    conn.close()

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('login.html')
        
        # Hash password for comparison
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute('SELECT id, username, is_admin FROM users WHERE username = ? AND password = ?', 
                 (username, hashed_password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['is_admin'] = user[2]
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form.get('email', '')
        
        # Validation
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('register.html')
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        # Hash password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            conn = sqlite3.connect('library.db')
            c = conn.cursor()
            c.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                     (username, hashed_password, email))
            conn.commit()
            conn.close()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists', 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    # Get statistics
    c.execute('SELECT COUNT(*) FROM books')
    total_books = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM books WHERE available = 1')
    available_books = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM borrowed WHERE return_date IS NULL')
    borrowed_books = c.fetchone()[0]
    
    conn.close()
    
    stats = {
        'total_books': total_books,
        'available_books': available_books,
        'borrowed_books': borrowed_books
    }
    
    return render_template('dashboard.html', stats=stats)

@app.route('/books')
@login_required
def books():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('SELECT * FROM books ORDER BY date_added DESC')
    books = c.fetchall()
    conn.close()
    
    return render_template('books.html', books=books)

@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form.get('author', '')
        isbn = request.form.get('isbn', '')
        
        if not title:
            flash('Book title is required', 'error')
            return render_template('add_book.html')
        
        try:
            conn = sqlite3.connect('library.db')
            c = conn.cursor()
            c.execute('INSERT INTO books (title, author, isbn) VALUES (?, ?, ?)',
                     (title, author, isbn))
            conn.commit()
            conn.close()
            
            flash('Book added successfully!', 'success')
            return redirect(url_for('books'))
        except sqlite3.IntegrityError:
            flash('A book with this title already exists', 'error')
    
    return render_template('add_book.html')

@app.route('/borrow', methods=['GET', 'POST'])
@login_required
def borrow():
    if request.method == 'POST':
        student_name = request.form['student_name']
        book_title = request.form['book_title']
        
        if not student_name or not book_title:
            flash('Student name and book title are required', 'error')
            return redirect(url_for('borrow'))
        
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        
        # Check if book is available
        c.execute('SELECT available FROM books WHERE title = ?', (book_title,))
        book = c.fetchone()
        
        if not book or book[0] == 0:
            flash('Book is not available for borrowing', 'error')
            conn.close()
            return redirect(url_for('borrow'))
        
        # Record the borrowing
        c.execute('INSERT INTO borrowed (student_name, book_title) VALUES (?, ?)',
                 (student_name, book_title))
        
        # Update book availability
        c.execute('UPDATE books SET available = 0 WHERE title = ?', (book_title,))
        
        conn.commit()
        conn.close()
        
        flash('Book borrowed successfully!', 'success')
        return redirect(url_for('borrowed_books'))
    
    # Get available books for the form
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('SELECT title FROM books WHERE available = 1 ORDER BY title')
    available_books = [row[0] for row in c.fetchall()]
    conn.close()
    
    return render_template('borrow.html', available_books=available_books)

@app.route('/return_book', methods=['GET', 'POST'])
@login_required
def return_book():
    if request.method == 'POST':
        borrow_id = request.form['borrow_id']
        
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        
        # Get the borrowed book details
        c.execute('SELECT book_title FROM borrowed WHERE id = ? AND return_date IS NULL', (borrow_id,))
        book = c.fetchone()
        
        if not book:
            flash('Invalid borrow record', 'error')
            conn.close()
            return redirect(url_for('borrowed_books'))
        
        # Update return date
        c.execute('UPDATE borrowed SET return_date = ? WHERE id = ?',
                 (datetime.now(), borrow_id))
        
        # Make book available again
        c.execute('UPDATE books SET available = 1 WHERE title = ?', (book[0],))
        
        conn.commit()
        conn.close()
        
        flash('Book returned successfully!', 'success')
        return redirect(url_for('borrowed_books'))
    
    return redirect(url_for('borrowed_books'))

@app.route('/borrowed_books')
@login_required
def borrowed_books():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('''
        SELECT id, student_name, book_title, borrow_date, return_date 
        FROM borrowed 
        ORDER BY borrow_date DESC
    ''')
    borrowed = c.fetchall()
    conn.close()
    
    return render_template('borrowed_books.html', borrowed=borrowed)

@app.route('/generate_qr/<book_title>')
@login_required
def generate_qr_code(book_title):
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"Book: {book_title}")
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for display
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    qr_code_data = base64.b64encode(buffer.getvalue()).decode()
    
    return jsonify({'qr_code': qr_code_data})

if __name__ == '__main__':
    # Create QR codes directory if it doesn't exist
    if not os.path.exists("qr_codes"):
        os.makedirs("qr_codes")
    
    # Initialize database
    initialize_database()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=8080)