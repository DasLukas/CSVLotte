"""
Module for MenubarSettingsView: renders the settings dialog for language selection and other preferences.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Any, Callable
from ..utils.translation import TranslationMixin


class MenubarSettingsView(TranslationMixin):
    """
    View class responsible for displaying the settings dialog with language selection.
    """

    def __init__(self, parent: Any, on_language_change: Callable[[str], None] = None) -> None:
        """
        Initialize the MenubarSettingsView with the parent window.
        
        :param parent: The parent window
        :param on_language_change: Callback function called when language changes
        """
        # Initialize TranslationMixin
        super().__init__()
        
        self.parent = parent
        self.on_language_change = on_language_change
        
        # Load language settings
        self._load_language_settings()
        
        self._create_settings_window()

    def _create_settings_window(self) -> None:
        """
        Create and display the settings window.
        """
        self.settings_window = tk.Toplevel(self.parent)
        self.settings_window.title(self._get_text('settings_title'))
        self.settings_window.geometry('300x150')
        self.settings_window.resizable(False, False)
        self.settings_window.transient(self.parent)
        self.settings_window.grab_set()
        
        # Center the window
        self.settings_window.update_idletasks()
        x = (self.settings_window.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.settings_window.winfo_screenheight() // 2) - (150 // 2)
        self.settings_window.geometry(f'300x150+{x}+{y}')
        
        self._build_settings_ui()

    def _build_settings_ui(self) -> None:
        """
        Build the settings UI components.
        """
        # Main frame
        frame = tk.Frame(self.settings_window)
        frame.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Language selection
        tk.Label(frame, text=self._get_text('language_label')).pack(anchor='w', pady=(0, 5))
        
        self.language_var = tk.StringVar(value=self._get_current_language())
        language_frame = tk.Frame(frame)
        language_frame.pack(anchor='w', pady=(0, 20))
        
        tk.Radiobutton(language_frame, text=self._get_text('german'), 
                      variable=self.language_var, value='de').pack(anchor='w')
        tk.Radiobutton(language_frame, text=self._get_text('english'), 
                      variable=self.language_var, value='en').pack(anchor='w')
        
        # Buttons
        button_frame = tk.Frame(frame)
        button_frame.pack(fill='x')
        
        tk.Button(button_frame, text=self._get_text('save'), 
                 command=self._save_settings).pack(side='right', padx=(5, 0))
        tk.Button(button_frame, text=self._get_text('cancel'), 
                 command=self._cancel_settings).pack(side='right')

    def _save_settings(self) -> None:
        """
        Save the settings and close the dialog.
        """
        new_language = self.language_var.get()
        if new_language != self._get_current_language():
            self._set_language(new_language)  # This now automatically saves to config
            self.settings_window.destroy()
            
            # Call the callback if provided
            if self.on_language_change:
                self.on_language_change(new_language)
            
            messagebox.showinfo(
                self._get_text('restart_required'),
                self._get_text('restart_message')
            )
        else:
            self.settings_window.destroy()

    def _cancel_settings(self) -> None:
        """
        Cancel the settings dialog without saving.
        """
        self.settings_window.destroy()
