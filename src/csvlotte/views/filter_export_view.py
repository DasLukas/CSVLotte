"""
Module for FilterExportView: GUI dialog to select export options and save filtered CSV data.
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Any, Optional
from ..utils.translation import TranslationMixin

class FilterExportView(tk.Toplevel, TranslationMixin):
    """
    View class to prompt user for export settings and trigger CSV export of filtered data.
    """
    def __init__(self, parent: Any, controller: Any, default_dir: Optional[str] = None, default_name: Optional[str] = None, source_path: Optional[str] = None) -> None:
        """
        Initialize the export dialog window with default paths and names.

        Args:
            parent (Any): Parent GUI window.
            controller (Any): Controller handling the export logic.
            default_dir (Optional[str]): Default folder to save file.
            default_name (Optional[str]): Default filename.
            source_path (Optional[str]): Original file path to derive defaults.
        """
        # Initialize parent classes
        tk.Toplevel.__init__(self, parent)
        TranslationMixin.__init__(self)
        
        self.title(self._get_text('export_title'))
        self.grab_set()
        self.resizable(False, False)
        self.controller = controller
        if source_path:
            self.default_dir = os.path.dirname(source_path)
            base, ext = os.path.splitext(os.path.basename(source_path))
            self.default_name = f"{base}_filtered{ext}"
        else:
            self.default_dir = default_dir or os.getcwd()
            self.default_name = default_name or 'export_filtered.csv'
        self._build_ui()

    def _build_ui(self) -> None:
        """
        Build all export dialog widgets (labels, entries, buttons) and layout them.
        """
        # Label and entry for delimiter selection
        tk.Label(self, text=self._get_text('delimiter_label')).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.delim_var = tk.StringVar(value=';')
        delim_entry = tk.Entry(self, textvariable=self.delim_var, width=3)
        delim_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        # Label and combobox for encoding selection
        tk.Label(self, text=self._get_text('encoding_label')).grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.encoding_var = tk.StringVar(value='latin1')
        encoding_combo = ttk.Combobox(self, textvariable=self.encoding_var, values=['latin1', 'utf-8', 'cp1252', 'utf-16', 'iso-8859-1'], state='readonly', width=10)
        encoding_combo.grid(row=0, column=3, sticky='w', padx=5, pady=5)
        # Label and entry for export directory
        tk.Label(self, text=self._get_text('save_location_label')).grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.path_var = tk.StringVar(value=self.default_dir)
        path_entry = tk.Entry(self, textvariable=self.path_var, width=40)
        path_entry.grid(row=1, column=1, columnspan=2, sticky='w', padx=5, pady=5)
        # Button to open directory chooser dialog
        tk.Button(self, text=self._get_text('choose_folder'), command=self.choose_dir).grid(row=1, column=3, sticky='w', padx=5, pady=5)
        # Label and entry for file name
        tk.Label(self, text=self._get_text('filename_label')).grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.name_var = tk.StringVar(value=self.default_name)
        name_entry = tk.Entry(self, textvariable=self.name_var, width=30)
        name_entry.grid(row=2, column=1, columnspan=2, sticky='w', padx=5, pady=5)
        # Button to trigger export
        tk.Button(self, text=self._get_text('export_button'), command=self.do_export).grid(row=3, column=0, columnspan=4, pady=10)
        # Center the dialog on the parent window
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f'+{x}+{y}')

    def choose_dir(self) -> None:
        """
        Open a directory selection dialog to choose export folder.
        """
        dir_ = filedialog.askdirectory(initialdir=self.default_dir)
        if dir_:
            self.path_var.set(dir_)

    def do_export(self) -> None:
        """
        Execute the export using settings from the dialog and display success or error message.
        """
        import os
        out_path = os.path.join(self.path_var.get(), self.name_var.get())
        if os.path.exists(out_path):
            overwrite = messagebox.askyesno(self._get_text('file_exists_title'), self._get_text('file_exists_message').format(out_path))
            if not overwrite:
                return
        success, error_msg = self.controller.export_filtered(
            out_path,
            sep=self.delim_var.get(),
            encoding=self.encoding_var.get()
        )
        if success:
            messagebox.showinfo(self._get_text('export_success_title'), self._get_text('export_success_message').format(out_path))
            self.destroy()
        else:
            messagebox.showerror(self._get_text('error'), self._get_text('export_error_message').format(error_msg))
