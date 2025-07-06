# filepath: my_tk_app/main.py
from csvlotte.controllers.home_controller import HomeController
import tkinter as tk
from typing import NoReturn

def main() -> None:
    root = tk.Tk()
    app = HomeController(root)
    root.mainloop()

if __name__ == "__main__":
    main()