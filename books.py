# books.py
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os
from qr_module import generate_qr
from PIL import ImageTk, Image

def add_book_ui():
    win = tk.Toplevel()
    win.title("Add New Book")
    win.geometry("400x300")
    win.resizable(False, False)
    win.grab_set()  # Make window modal
    
    # Center the window
    win.eval('tk::PlaceWindow . center')
    
    # Main frame
    main_frame = tk.Frame(win, padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)
    
    # Title
    tk.Label(main_frame, text="Add New Book", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))
    
    # Form fields
    tk.Label(main_frame, text="Title *:", font=("Arial", 10)).grid(row=1, column=0, sticky="e", padx=(0, 10), pady=5)
    title_entry = tk.Entry(main_frame, font=("Arial", 10), width=25)
    title_entry.grid(row=1, column=1, pady=5)
    title_entry.focus()
    
    tk.Label(main_frame, text="Author:", font=("Arial", 10)).grid(row=2, column=0, sticky="e", padx=(0, 10), pady=5)
    author_entry = tk.Entry(main_frame, font=("Arial", 10), width=25)
    author_entry.grid(row=2, column=1, pady=5)
    
    tk.Label(main_frame, text="ISBN:", font=("Arial", 10)).grid(row=3, column=0, sticky="e", padx=(0, 10), pady=5)
    isbn_entry = tk.Entry(main_frame, font=("Arial", 10), width=25)
    isbn_entry.grid(row=3, column=1, pady=5)
    
    # Required field note
    tk.Label(main_frame, text="* Required field", font=("Arial", 8), fg="red").grid(row=4, column=0, columnspan=2, pady=5)

    def save_book():
        title = title_entry.get().strip()
        author = author_entry.get().strip()
        isbn = isbn_entry.get().strip()
        
        if not title:
            messagebox.showerror("Error", "Title is required")
            title_entry.focus()
            return

        try:
            conn = sqlite3.connect("library.db")
            c = conn.cursor()
            
            # Check if book already exists
            c.execute("SELECT id FROM books WHERE title = ?", (title,))
            if c.fetchone():
                messagebox.showerror("Error", "A book with this title already exists")
                title_entry.focus()
                return
            
            # Insert new book
            c.execute("INSERT INTO books (title, author, isbn) VALUES (?, ?, ?)", 
                     (title, author if author else None, isbn if isbn else None))
            conn.commit()
            
            # Generate QR code
            qr_filename = f"qr_codes/{title.replace(' ', '_').replace('/', '_')}_qr.png"
            generate_qr(f"Book: {title}\nAuthor: {author}\nISBN: {isbn}", qr_filename)
            
            messagebox.showinfo("Success", f"Book '{title}' added successfully!\nQR code saved as: {qr_filename}")
            win.destroy()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error saving book: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def on_enter(event):
        save_book()
    
    # Bind Enter key
    win.bind('<Return>', on_enter)
    
    # Buttons frame
    button_frame = tk.Frame(main_frame)
    button_frame.grid(row=5, column=0, columnspan=2, pady=20)
    
    tk.Button(button_frame, text="Save Book", command=save_book, 
              font=("Arial", 10), bg="#3498db", fg="white", width=12).pack(side="left", padx=5)
    tk.Button(button_frame, text="Cancel", command=win.destroy, 
              font=("Arial", 10), bg="#95a5a6", fg="white", width=12).pack(side="left", padx=5)

def view_books_ui():
    win = tk.Toplevel()
    win.title("All Books")
    win.geometry("800x500")
    win.grab_set()
    
    # Main frame
    main_frame = tk.Frame(win, padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)
    
    # Title
    tk.Label(main_frame, text="All Books in Library", font=("Arial", 14, "bold")).pack(pady=(0, 20))
    
    # Create Treeview for displaying books
    columns = ("ID", "Title", "Author", "ISBN", "Available", "Date Added")
    tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
    
    # Define headings
    tree.heading("ID", text="ID")
    tree.heading("Title", text="Title")
    tree.heading("Author", text="Author")
    tree.heading("ISBN", text="ISBN")
    tree.heading("Available", text="Available")
    tree.heading("Date Added", text="Date Added")
    
    # Configure column widths
    tree.column("ID", width=50)
    tree.column("Title", width=200)
    tree.column("Author", width=150)
    tree.column("ISBN", width=120)
    tree.column("Available", width=80)
    tree.column("Date Added", width=120)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    # Pack tree and scrollbar
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Load books data
    def load_books():
        # Clear existing data
        for item in tree.get_children():
            tree.delete(item)
        
        try:
            conn = sqlite3.connect("library.db")
            c = conn.cursor()
            c.execute("SELECT id, title, author, isbn, available, date_added FROM books ORDER BY title")
            books = c.fetchall()
            
            for book in books:
                # Format the data
                book_id, title, author, isbn, available, date_added = book
                author = author if author else "N/A"
                isbn = isbn if isbn else "N/A"
                available_text = "Yes" if available else "No"
                date_added = date_added.split()[0] if date_added else "N/A"  # Show only date part
                
                tree.insert("", "end", values=(book_id, title, author, isbn, available_text, date_added))
            
            # Update status
            status_label.config(text=f"Total books: {len(books)}")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading books: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    # Status frame
    status_frame = tk.Frame(main_frame)
    status_frame.pack(fill="x", pady=(10, 0))
    
    status_label = tk.Label(status_frame, text="Loading...", font=("Arial", 10))
    status_label.pack(side="left")
    
    # Buttons
    button_frame = tk.Frame(status_frame)
    button_frame.pack(side="right")
    
    tk.Button(button_frame, text="Refresh", command=load_books, 
              font=("Arial", 10), bg="#3498db", fg="white").pack(side="left", padx=5)
    tk.Button(button_frame, text="Close", command=win.destroy, 
              font=("Arial", 10), bg="#95a5a6", fg="white").pack(side="left", padx=5)
    
    # Load initial data
    load_books()
