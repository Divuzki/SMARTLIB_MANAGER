# login.py
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import hashlib
import config

def initialize_users_table():
    """Initialize users table for registration system"""
    try:
        conn = sqlite3.connect(config.DATABASE_NAME)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'user',
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default admin if not exists
        admin_hash = hashlib.sha256(config.ADMIN_PASSWORD.encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                 (config.ADMIN_USERNAME, admin_hash, 'admin'))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error initializing users table: {e}")

def show_login(callback):
    # Initialize users table
    initialize_users_table()
    
    # Create root window for login
    login_window = tk.Tk()
    login_window.title("SMARTLIB MANAGER - Login")
    login_window.geometry("450x400")
    login_window.resizable(False, False)
    login_window.configure(bg=config.WINDOW_THEME['background_color'])
    
    # Center the window
    login_window.eval('tk::PlaceWindow . center')

    # Create notebook for tabs
    notebook = ttk.Notebook(login_window)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Login Tab
    login_frame = tk.Frame(notebook, bg=config.WINDOW_THEME['background_color'])
    notebook.add(login_frame, text="Login")
    
    # Registration Tab
    register_frame = tk.Frame(notebook, bg=config.WINDOW_THEME['background_color'])
    notebook.add(register_frame, text="Register")
    
    # === LOGIN TAB ===
    login_main_frame = tk.Frame(login_frame, padx=20, pady=20, bg=config.WINDOW_THEME['background_color'])
    login_main_frame.pack(fill="both", expand=True)
    
    # Login form with improved visibility
    tk.Label(login_main_frame, text="Username:", font=(config.FONT_FAMILY, config.FONT_SIZE_MEDIUM, 'bold'), 
             bg=config.WINDOW_THEME['background_color'], fg='#1565C0').grid(row=0, column=0, sticky="e", padx=(0, 10), pady=12)
    tk.Label(login_main_frame, text="Password:", font=(config.FONT_FAMILY, config.FONT_SIZE_MEDIUM, 'bold'), 
             bg=config.WINDOW_THEME['background_color'], fg='#1565C0').grid(row=1, column=0, sticky="e", padx=(0, 10), pady=12)

    login_username_entry = tk.Entry(login_main_frame, font=(config.FONT_FAMILY, config.FONT_SIZE_MEDIUM), width=18,
                                   bg='#F8F9FA', fg='black', insertbackground='black', relief='solid', bd=2, highlightthickness=2, highlightcolor=config.WINDOW_THEME['primary_color'], highlightbackground='#E3F2FD')
    login_password_entry = tk.Entry(login_main_frame, show="*", font=(config.FONT_FAMILY, config.FONT_SIZE_MEDIUM), width=18,
                                   bg='#F8F9FA', fg='black', insertbackground='black', relief='solid', bd=2, highlightthickness=2, highlightcolor=config.WINDOW_THEME['primary_color'], highlightbackground='#E3F2FD')
    login_username_entry.grid(row=0, column=1, pady=12, padx=10, ipady=4)
    login_password_entry.grid(row=1, column=1, pady=12, padx=10, ipady=4)
    
    # Set focus to username entry
    login_username_entry.focus()

    def verify_login():
        user = login_username_entry.get().strip()
        pwd = login_password_entry.get().strip()
        
        if not user or not pwd:
            messagebox.showerror("Login Failed", "Please enter both username and password")
            return
        
        try:
            conn = sqlite3.connect(config.DATABASE_NAME)
            c = conn.cursor()
            
            # Hash the entered password
            pwd_hash = hashlib.sha256(pwd.encode()).hexdigest()
            
            # Check credentials in database
            c.execute("SELECT role FROM users WHERE username = ? AND password_hash = ?", (user, pwd_hash))
            result = c.fetchone()
            
            if result:
                role = result[0]
                messagebox.showinfo("Login", f"Login Successful! Welcome {user} ({role})")
                login_window.destroy()
                callback()
            else:
                messagebox.showerror("Login Failed", "Invalid credentials")
                login_password_entry.delete(0, tk.END)  # Clear password field
                login_username_entry.focus()
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")
            login_password_entry.delete(0, tk.END)
            login_username_entry.focus()
    
    def on_login_enter(event):
        verify_login()

    # Bind Enter key to login
    login_username_entry.bind('<Return>', on_login_enter)
    login_password_entry.bind('<Return>', on_login_enter)

    login_btn = tk.Button(login_main_frame, text="Login", command=verify_login, 
                         font=(config.FONT_FAMILY, config.FONT_SIZE_MEDIUM, 'bold'), 
                         bg=config.WINDOW_THEME['success_color'], fg="white", width=15, relief='flat',
                         cursor='hand2', activebackground='#27ae60', activeforeground='white')
    login_btn.grid(row=2, column=0, columnspan=2, pady=20, ipady=6)
    
    # === REGISTRATION TAB ===
    register_main_frame = tk.Frame(register_frame, padx=20, pady=20, bg=config.WINDOW_THEME['background_color'])
    register_main_frame.pack(fill="both", expand=True)
    
    # Registration form with improved visibility
    tk.Label(register_main_frame, text="Username:", font=(config.FONT_FAMILY, config.FONT_SIZE_MEDIUM, 'bold'), 
             bg=config.WINDOW_THEME['background_color'], fg='#1565C0').grid(row=0, column=0, sticky="e", padx=(0, 10), pady=10)
    tk.Label(register_main_frame, text="Password:", font=(config.FONT_FAMILY, config.FONT_SIZE_MEDIUM, 'bold'), 
             bg=config.WINDOW_THEME['background_color'], fg='#1565C0').grid(row=1, column=0, sticky="e", padx=(0, 10), pady=10)
    tk.Label(register_main_frame, text="Confirm Password:", font=(config.FONT_FAMILY, config.FONT_SIZE_MEDIUM, 'bold'), 
             bg=config.WINDOW_THEME['background_color'], fg='#1565C0').grid(row=2, column=0, sticky="e", padx=(0, 10), pady=10)
    tk.Label(register_main_frame, text="Email (Optional):", font=(config.FONT_FAMILY, config.FONT_SIZE_MEDIUM, 'bold'), 
             bg=config.WINDOW_THEME['background_color'], fg='#1565C0').grid(row=3, column=0, sticky="e", padx=(0, 10), pady=10)

    reg_username_entry = tk.Entry(register_main_frame, font=(config.FONT_FAMILY, config.FONT_SIZE_MEDIUM), width=18,
                                 bg='#F8F9FA', fg='black', insertbackground='black', relief='solid', bd=2, highlightthickness=2, highlightcolor=config.WINDOW_THEME['primary_color'], highlightbackground='#E3F2FD')
    reg_password_entry = tk.Entry(register_main_frame, show="*", font=(config.FONT_FAMILY, config.FONT_SIZE_MEDIUM), width=18,
                                 bg='#F8F9FA', fg='black', insertbackground='black', relief='solid', bd=2, highlightthickness=2, highlightcolor=config.WINDOW_THEME['primary_color'], highlightbackground='#E3F2FD')
    reg_confirm_entry = tk.Entry(register_main_frame, show="*", font=(config.FONT_FAMILY, config.FONT_SIZE_MEDIUM), width=18,
                                bg='#F8F9FA', fg='black', insertbackground='black', relief='solid', bd=2, highlightthickness=2, highlightcolor=config.WINDOW_THEME['primary_color'], highlightbackground='#E3F2FD')
    reg_email_entry = tk.Entry(register_main_frame, font=(config.FONT_FAMILY, config.FONT_SIZE_MEDIUM), width=18,
                              bg='#F8F9FA', fg='black', insertbackground='black', relief='solid', bd=2, highlightthickness=2, highlightcolor=config.WINDOW_THEME['primary_color'], highlightbackground='#E3F2FD')
    
    reg_username_entry.grid(row=0, column=1, pady=10, padx=10, ipady=4)
    reg_password_entry.grid(row=1, column=1, pady=10, padx=10, ipady=4)
    reg_confirm_entry.grid(row=2, column=1, pady=10, padx=10, ipady=4)
    reg_email_entry.grid(row=3, column=1, pady=10, padx=10, ipady=4)
    
    def register_user():
        username = reg_username_entry.get().strip()
        password = reg_password_entry.get().strip()
        confirm_password = reg_confirm_entry.get().strip()
        email = reg_email_entry.get().strip()
        
        # Validation
        if not username or not password:
            messagebox.showerror("Registration Failed", "Username and password are required")
            return
            
        if len(username) < 3:
            messagebox.showerror("Registration Failed", "Username must be at least 3 characters long")
            return
            
        if len(password) < 6:
            messagebox.showerror("Registration Failed", "Password must be at least 6 characters long")
            return
            
        if password != confirm_password:
            messagebox.showerror("Registration Failed", "Passwords do not match")
            return
        
        try:
            conn = sqlite3.connect(config.DATABASE_NAME)
            c = conn.cursor()
            
            # Check if username already exists
            c.execute("SELECT username FROM users WHERE username = ?", (username,))
            if c.fetchone():
                messagebox.showerror("Registration Failed", "Username already exists")
                conn.close()
                return
            
            # Hash password and insert user
            pwd_hash = hashlib.sha256(password.encode()).hexdigest()
            c.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                     (username, pwd_hash, email if email else None))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Registration Successful", "Account created successfully! You can now login.")
            
            # Clear registration form and switch to login tab
            reg_username_entry.delete(0, tk.END)
            reg_password_entry.delete(0, tk.END)
            reg_confirm_entry.delete(0, tk.END)
            reg_email_entry.delete(0, tk.END)
            notebook.select(0)  # Switch to login tab
            
        except Exception as e:
            messagebox.showerror("Error", f"Registration failed: {e}")
    
    def on_register_enter(event):
        register_user()
    
    # Bind Enter key to registration
    reg_username_entry.bind('<Return>', on_register_enter)
    reg_password_entry.bind('<Return>', on_register_enter)
    reg_confirm_entry.bind('<Return>', on_register_enter)
    reg_email_entry.bind('<Return>', on_register_enter)
    
    register_btn = tk.Button(register_main_frame, text="Register", command=register_user, 
                            font=(config.FONT_FAMILY, config.FONT_SIZE_MEDIUM, 'bold'), 
                            bg=config.WINDOW_THEME['primary_color'], fg="white", width=15, relief='flat',
                            cursor='hand2', activebackground='#2980b9', activeforeground='white')
    register_btn.grid(row=4, column=0, columnspan=2, pady=20, ipady=6)
    
    # Handle window close
    def on_closing():
        login_window.quit()
        login_window.destroy()
    
    login_window.protocol("WM_DELETE_WINDOW", on_closing)
    login_window.mainloop()
