# borrow_return.py
import tkinter as tk
from tkinter import messagebox
import sqlite3

def borrow_ui():
    win = tk.Toplevel()
    win.title("Borrow Book")

    tk.Label(win, text="Student Name").grid(row=0, column=0)
    tk.Label(win, text="Book Title").grid(row=1, column=0)
    sname = tk.Entry(win)
    btitle = tk.Entry(win)
    sname.grid(row=0, column=1)
    btitle.grid(row=1, column=1)

    def borrow():
        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS borrowed (student TEXT, book TEXT)")
        c.execute("INSERT INTO borrowed VALUES (?, ?)", (sname.get(), btitle.get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Book borrowed.")
        win.destroy()

    tk.Button(win, text="Submit", command=borrow).grid(row=2, column=1)

def return_ui():
    win = tk.Toplevel()
    win.title("Return Book")

    tk.Label(win, text="Student Name").grid(row=0, column=0)
    tk.Label(win, text="Book Title").grid(row=1, column=0)
    sname = tk.Entry(win)
    btitle = tk.Entry(win)
    sname.grid(row=0, column=1)
    btitle.grid(row=1, column=1)

    def ret():
        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        c.execute("DELETE FROM borrowed WHERE student = ? AND book = ?", (sname.get(), btitle.get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Book returned.")
        win.destroy()

    tk.Button(win, text="Submit", command=ret).grid(row=2, column=1)
