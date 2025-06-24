# main.py
import tkinter as tk
from tkinter import messagebox
import sqlite3
import os
from login import show_login
from books import add_book_ui, view_books_ui
from borrow_return import borrow_ui, return_ui, view_borrowed_books_ui

def initialize_database():
    """Initialize the database with required tables"""
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

def main_app():
    # Initialize database
    initialize_database()
    
    # Create QR codes directory if it doesn't exist
    if not os.path.exists("qr_codes"):
        os.makedirs("qr_codes")
    
    root = tk.Tk()
    root.title("SMARTLIB MANAGER - Main Dashboard")
    root.geometry("500x400")
    root.resizable(False, False)
    
    # Center the window
    root.eval('tk::PlaceWindow . center')
    
    # Main frame
    main_frame = tk.Frame(root, bg="#f0f0f0", padx=30, pady=30)
    main_frame.pack(fill="both", expand=True)
    
    # Title
    title_label = tk.Label(main_frame, text="SMARTLIB MANAGER", 
                          font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#2c3e50")
    title_label.pack(pady=(0, 20))
    
    # Subtitle
    subtitle_label = tk.Label(main_frame, text="Library Management System", 
                             font=("Arial", 10), bg="#f0f0f0", fg="#7f8c8d")
    subtitle_label.pack(pady=(0, 30))
    
    # Button style configuration
    button_config = {
        "font": ("Arial", 11),
        "width": 25,
        "height": 2,
        "relief": "flat",
        "cursor": "hand2"
    }
    
    # Book Management Section
    book_frame = tk.LabelFrame(main_frame, text="Book Management", 
                              font=("Arial", 10, "bold"), bg="#f0f0f0", padx=10, pady=10)
    book_frame.pack(fill="x", pady=(0, 15))
    
    tk.Button(book_frame, text="📚 Add New Book", bg="#3498db", fg="white", 
              command=add_book_ui, **button_config).pack(pady=5)
    tk.Button(book_frame, text="📖 View All Books", bg="#2ecc71", fg="white", 
              command=view_books_ui, **button_config).pack(pady=5)
    
    # Transaction Section
    transaction_frame = tk.LabelFrame(main_frame, text="Book Transactions", 
                                     font=("Arial", 10, "bold"), bg="#f0f0f0", padx=10, pady=10)
    transaction_frame.pack(fill="x", pady=(0, 15))
    
    tk.Button(transaction_frame, text="📤 Borrow Book", bg="#e74c3c", fg="white", 
              command=borrow_ui, **button_config).pack(pady=5)
    tk.Button(transaction_frame, text="📥 Return Book", bg="#f39c12", fg="white", 
              command=return_ui, **button_config).pack(pady=5)
    tk.Button(transaction_frame, text="📋 View Borrowed Books", bg="#9b59b6", fg="white", 
              command=view_borrowed_books_ui, **button_config).pack(pady=5)
    
    # Exit button
    def on_exit():
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            root.quit()
            root.destroy()
    
    tk.Button(main_frame, text="❌ Exit", bg="#95a5a6", fg="white", 
              command=on_exit, font=("Arial", 10), width=15).pack(pady=20)
    
    # Handle window close
    root.protocol("WM_DELETE_WINDOW", on_exit)
    
    root.mainloop()

if __name__ == "__main__":
    show_login(main_app)
