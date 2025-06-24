# books.py
import tkinter as tk
from tkinter import messagebox
import sqlite3
from qr_module import generate_qr
from PIL import ImageTk, Image

def add_book_ui():
    win = tk.Toplevel()
    win.title("Add New Book")

    tk.Label(win, text="Title").grid(row=0, column=0)
    title_entry = tk.Entry(win)
    title_entry.grid(row=0, column=1)

    def save_book():
        title = title_entry.get()
        if not title:
            messagebox.showerror("Error", "Title is required")
            return

        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, title TEXT)")
        c.execute("INSERT INTO books (title) VALUES (?)", (title,))
        conn.commit()
        conn.close()

        generate_qr(title, f"{title}.png")
        messagebox.showinfo("Saved", f"Book '{title}' added with QR code.")
        win.destroy()

    tk.Button(win, text="Save Book", command=save_book).grid(row=1, column=1)
