# login.py
import tkinter as tk
from tkinter import messagebox
import config

def show_login(callback):
    # Create root window for login
    login_window = tk.Tk()
    login_window.title("SMARTLIB MANAGER - Admin Login")
    login_window.geometry("300x150")
    login_window.resizable(False, False)
    
    # Center the window
    login_window.eval('tk::PlaceWindow . center')

    # Create and place widgets with better layout
    main_frame = tk.Frame(login_window, padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)
    
    tk.Label(main_frame, text="Username:", font=("Arial", 10)).grid(row=0, column=0, sticky="e", padx=(0, 10), pady=5)
    tk.Label(main_frame, text="Password:", font=("Arial", 10)).grid(row=1, column=0, sticky="e", padx=(0, 10), pady=5)

    username_entry = tk.Entry(main_frame, font=("Arial", 10), width=15)
    password_entry = tk.Entry(main_frame, show="*", font=("Arial", 10), width=15)
    username_entry.grid(row=0, column=1, pady=5)
    password_entry.grid(row=1, column=1, pady=5)
    
    # Set focus to username entry
    username_entry.focus()

    def verify():
        user = username_entry.get().strip()
        pwd = password_entry.get().strip()
        
        if not user or not pwd:
            messagebox.showerror("Login Failed", "Please enter both username and password")
            return
            
        if user == config.ADMIN_USERNAME and pwd == config.ADMIN_PASSWORD:
            messagebox.showinfo("Login", "Login Successful")
            login_window.destroy()
            callback()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")
            password_entry.delete(0, tk.END)  # Clear password field
            username_entry.focus()
    
    def on_enter(event):
        verify()

    # Bind Enter key to login
    login_window.bind('<Return>', on_enter)
    username_entry.bind('<Return>', on_enter)
    password_entry.bind('<Return>', on_enter)

    login_btn = tk.Button(main_frame, text="Login", command=verify, font=("Arial", 10), bg="#4CAF50", fg="white", width=10)
    login_btn.grid(row=2, column=0, columnspan=2, pady=15)
    
    # Handle window close
    def on_closing():
        login_window.quit()
        login_window.destroy()
    
    login_window.protocol("WM_DELETE_WINDOW", on_closing)
    login_window.mainloop()
