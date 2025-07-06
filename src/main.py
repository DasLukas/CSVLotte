"""
Main entrypoint for the CSVLotte application. Initializes the GUI and starts the Tkinter main loop.
"""

from csvlotte.controllers.home_controller import HomeController
import tkinter as tk
from typing import NoReturn

def main() -> None:
    """
    Initialize HomeController and start the Tkinter event loop.

    Returns:
        None
    """
    root = tk.Tk()
    app = HomeController(root)
    root.mainloop()

if __name__ == "__main__":
    main()