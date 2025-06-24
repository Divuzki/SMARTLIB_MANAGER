# borrow_return.py
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

def borrow_ui():
    win = tk.Toplevel()
    win.title("Borrow Book")
    win.geometry("450x350")
    win.resizable(False, False)
    win.grab_set()
    
    # Center the window
    win.eval('tk::PlaceWindow . center')
    
    # Main frame
    main_frame = tk.Frame(win, padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)
    
    # Title
    tk.Label(main_frame, text="Borrow Book", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))
    
    # Form fields
    tk.Label(main_frame, text="Student Name *:", font=("Arial", 10)).grid(row=1, column=0, sticky="e", padx=(0, 10), pady=5)
    sname = tk.Entry(main_frame, font=("Arial", 10), width=25)
    sname.grid(row=1, column=1, pady=5)
    sname.focus()
    
    tk.Label(main_frame, text="Book Title *:", font=("Arial", 10)).grid(row=2, column=0, sticky="e", padx=(0, 10), pady=5)
    
    # Use Combobox for book selection
    btitle = ttk.Combobox(main_frame, font=("Arial", 10), width=23, state="readonly")
    btitle.grid(row=2, column=1, pady=5)
    
    # Load available books
    def load_available_books():
        try:
            conn = sqlite3.connect("library.db")
            c = conn.cursor()
            c.execute("SELECT title FROM books WHERE available = 1 ORDER BY title")
            books = [row[0] for row in c.fetchall()]
            btitle['values'] = books
            if books:
                btitle.set("Select a book...")
            else:
                btitle.set("No books available")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading books: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    load_available_books()
    
    # Required field note
    tk.Label(main_frame, text="* Required fields", font=("Arial", 8), fg="red").grid(row=3, column=0, columnspan=2, pady=5)
    
    # Available books info
    info_frame = tk.LabelFrame(main_frame, text="Available Books", font=("Arial", 9))
    info_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)
    
    refresh_btn = tk.Button(info_frame, text="Refresh List", command=load_available_books, 
                           font=("Arial", 9), bg="#3498db", fg="white")
    refresh_btn.pack(pady=5)

    def borrow():
        student_name = sname.get().strip()
        book_title = btitle.get().strip()
        
        if not student_name or not book_title or book_title == "Select a book..." or book_title == "No books available":
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        try:
            conn = sqlite3.connect("library.db")
            c = conn.cursor()
            
            # Check if book is still available
            c.execute("SELECT available FROM books WHERE title = ?", (book_title,))
            result = c.fetchone()
            if not result or result[0] == 0:
                messagebox.showerror("Error", "This book is no longer available")
                load_available_books()  # Refresh the list
                return
            
            # Check if student already borrowed this book
            c.execute("SELECT id FROM borrowed WHERE student_name = ? AND book_title = ? AND return_date IS NULL", 
                     (student_name, book_title))
            if c.fetchone():
                messagebox.showerror("Error", "This student has already borrowed this book")
                return
            
            # Record the borrowing
            c.execute("INSERT INTO borrowed (student_name, book_title) VALUES (?, ?)", 
                     (student_name, book_title))
            
            # Mark book as unavailable
            c.execute("UPDATE books SET available = 0 WHERE title = ?", (book_title,))
            
            conn.commit()
            messagebox.showinfo("Success", f"Book '{book_title}' borrowed by {student_name}")
            win.destroy()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error processing borrow request: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def on_enter(event):
        borrow()
    
    # Bind Enter key
    win.bind('<Return>', on_enter)
    
    # Buttons frame
    button_frame = tk.Frame(main_frame)
    button_frame.grid(row=5, column=0, columnspan=2, pady=20)
    
    tk.Button(button_frame, text="Borrow Book", command=borrow, 
              font=("Arial", 10), bg="#e74c3c", fg="white", width=12).pack(side="left", padx=5)
    tk.Button(button_frame, text="Cancel", command=win.destroy, 
              font=("Arial", 10), bg="#95a5a6", fg="white", width=12).pack(side="left", padx=5)

def return_ui():
    win = tk.Toplevel()
    win.title("Return Book")
    win.geometry("450x350")
    win.resizable(False, False)
    win.grab_set()
    
    # Center the window
    win.eval('tk::PlaceWindow . center')
    
    # Main frame
    main_frame = tk.Frame(win, padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)
    
    # Title
    tk.Label(main_frame, text="Return Book", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))
    
    # Form fields
    tk.Label(main_frame, text="Student Name *:", font=("Arial", 10)).grid(row=1, column=0, sticky="e", padx=(0, 10), pady=5)
    sname = tk.Entry(main_frame, font=("Arial", 10), width=25)
    sname.grid(row=1, column=1, pady=5)
    sname.focus()
    
    tk.Label(main_frame, text="Book Title *:", font=("Arial", 10)).grid(row=2, column=0, sticky="e", padx=(0, 10), pady=5)
    
    # Use Combobox for borrowed book selection
    btitle = ttk.Combobox(main_frame, font=("Arial", 10), width=23, state="readonly")
    btitle.grid(row=2, column=1, pady=5)
    
    # Load borrowed books for the student
    def load_borrowed_books():
        student_name = sname.get().strip()
        if not student_name:
            btitle['values'] = []
            btitle.set("Enter student name first")
            return
        
        try:
            conn = sqlite3.connect("library.db")
            c = conn.cursor()
            c.execute("SELECT book_title FROM borrowed WHERE student_name = ? AND return_date IS NULL", 
                     (student_name,))
            books = [row[0] for row in c.fetchall()]
            btitle['values'] = books
            if books:
                btitle.set("Select a book...")
            else:
                btitle.set("No borrowed books found")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading borrowed books: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    # Bind student name entry to load books
    def on_student_change(event):
        win.after(500, load_borrowed_books)  # Delay to avoid too many calls
    
    sname.bind('<KeyRelease>', on_student_change)
    
    # Required field note
    tk.Label(main_frame, text="* Required fields", font=("Arial", 8), fg="red").grid(row=3, column=0, columnspan=2, pady=5)
    
    # Info frame
    info_frame = tk.LabelFrame(main_frame, text="Instructions", font=("Arial", 9))
    info_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)
    
    tk.Label(info_frame, text="1. Enter student name\n2. Select book from dropdown", 
             font=("Arial", 9), justify="left").pack(pady=5)

    def ret():
        student_name = sname.get().strip()
        book_title = btitle.get().strip()
        
        if not student_name or not book_title or book_title in ["Select a book...", "No borrowed books found", "Enter student name first"]:
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        try:
            conn = sqlite3.connect("library.db")
            c = conn.cursor()
            
            # Check if the borrowing record exists
            c.execute("SELECT id FROM borrowed WHERE student_name = ? AND book_title = ? AND return_date IS NULL", 
                     (student_name, book_title))
            borrow_record = c.fetchone()
            
            if not borrow_record:
                messagebox.showerror("Error", "No active borrowing record found for this student and book")
                return
            
            # Update the borrowing record with return date
            c.execute("UPDATE borrowed SET return_date = ? WHERE id = ?", 
                     (datetime.now().isoformat(), borrow_record[0]))
            
            # Mark book as available
            c.execute("UPDATE books SET available = 1 WHERE title = ?", (book_title,))
            
            conn.commit()
            messagebox.showinfo("Success", f"Book '{book_title}' returned by {student_name}")
            win.destroy()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error processing return: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def on_enter(event):
        ret()
    
    # Bind Enter key
    win.bind('<Return>', on_enter)
    
    # Buttons frame
    button_frame = tk.Frame(main_frame)
    button_frame.grid(row=5, column=0, columnspan=2, pady=20)
    
    tk.Button(button_frame, text="Return Book", command=ret, 
              font=("Arial", 10), bg="#f39c12", fg="white", width=12).pack(side="left", padx=5)
    tk.Button(button_frame, text="Cancel", command=win.destroy, 
              font=("Arial", 10), bg="#95a5a6", fg="white", width=12).pack(side="left", padx=5)

def view_borrowed_books_ui():
    win = tk.Toplevel()
    win.title("Borrowed Books")
    win.geometry("900x500")
    win.grab_set()
    
    # Main frame
    main_frame = tk.Frame(win, padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)
    
    # Title
    tk.Label(main_frame, text="Currently Borrowed Books", font=("Arial", 14, "bold")).pack(pady=(0, 20))
    
    # Create Treeview for displaying borrowed books
    columns = ("ID", "Student Name", "Book Title", "Borrow Date", "Days Borrowed")
    tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
    
    # Define headings
    tree.heading("ID", text="ID")
    tree.heading("Student Name", text="Student Name")
    tree.heading("Book Title", text="Book Title")
    tree.heading("Borrow Date", text="Borrow Date")
    tree.heading("Days Borrowed", text="Days Borrowed")
    
    # Configure column widths
    tree.column("ID", width=50)
    tree.column("Student Name", width=200)
    tree.column("Book Title", width=250)
    tree.column("Borrow Date", width=150)
    tree.column("Days Borrowed", width=120)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    # Pack tree and scrollbar
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Load borrowed books data
    def load_borrowed_books():
        # Clear existing data
        for item in tree.get_children():
            tree.delete(item)
        
        try:
            conn = sqlite3.connect("library.db")
            c = conn.cursor()
            c.execute("SELECT id, student_name, book_title, borrow_date FROM borrowed WHERE return_date IS NULL ORDER BY borrow_date DESC")
            borrowed_books = c.fetchall()
            
            for book in borrowed_books:
                book_id, student_name, book_title, borrow_date = book
                
                # Calculate days borrowed
                try:
                    borrow_datetime = datetime.fromisoformat(borrow_date)
                    days_borrowed = (datetime.now() - borrow_datetime).days
                except:
                    days_borrowed = "N/A"
                
                # Format borrow date
                try:
                    formatted_date = datetime.fromisoformat(borrow_date).strftime("%Y-%m-%d %H:%M")
                except:
                    formatted_date = borrow_date
                
                tree.insert("", "end", values=(book_id, student_name, book_title, formatted_date, days_borrowed))
            
            # Update status
            status_label.config(text=f"Total borrowed books: {len(borrowed_books)}")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading borrowed books: {str(e)}")
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
    
    tk.Button(button_frame, text="Refresh", command=load_borrowed_books, 
              font=("Arial", 10), bg="#3498db", fg="white").pack(side="left", padx=5)
    tk.Button(button_frame, text="Close", command=win.destroy, 
              font=("Arial", 10), bg="#95a5a6", fg="white").pack(side="left", padx=5)
    
    # Load initial data
    load_borrowed_books()
