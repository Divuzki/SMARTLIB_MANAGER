# login.py
import tkinter as tk
from tkinter import messagebox
import config

def show_login(callback):
    login_window = tk.Toplevel()
    login_window.title("Admin Login")

    tk.Label(login_window, text="Username:").grid(row=0, column=0)
    tk.Label(login_window, text="Password:").grid(row=1, column=0)

    username_entry = tk.Entry(login_window)
    password_entry = tk.Entry(login_window, show="*")
    username_entry.grid(row=0, column=1)
    password_entry.grid(row=1, column=1)

    def verify():
        user = username_entry.get()
        pwd = password_entry.get()
        if user == config.ADMIN_USERNAME and pwd == config.ADMIN_PASSWORD:
            messagebox.showinfo("Login", "Login Successful")
            login_window.destroy()
            callback()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")

    tk.Button(login_window, text="Login", command=verify).grid(row=2, column=1)
