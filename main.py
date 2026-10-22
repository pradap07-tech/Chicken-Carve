import tkinter as tk
from tkinter import messagebox

from database import DatabaseManager
from backend import BackendService
from frontend import ChickenCraveApp


def main():
    root = tk.Tk()

    db = DatabaseManager("chicken_crave.db")
    backend = BackendService(db)

    try:
        app = ChickenCraveApp(root, backend)
    except Exception as exc:
        messagebox.showerror("Chicken Crave Startup Error", str(exc))
        db.close()
        root.destroy()
        raise

    def on_close():
        db.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
