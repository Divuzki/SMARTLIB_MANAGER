# main.py
import tkinter as tk
from login import show_login
from books import add_book_ui
from borrow_return import borrow_ui, return_ui

def main_app():
    root = tk.Tk()
    root.title("SMARTLIB MANAGER")

    tk.Button(root, text="Register Book", width=30, command=add_book_ui).pack(pady=5)
    tk.Button(root, text="Borrow Book", width=30, command=borrow_ui).pack(pady=5)
    tk.Button(root, text="Return Book", width=30, command=return_ui).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    show_login(main_app)
