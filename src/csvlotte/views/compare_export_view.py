"""
Module for CompareExportView: GUI dialog to configure and export comparison results to CSV files.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Any, List, Optional
import os
from ..utils.translation import TranslationMixin

class CompareExportView(tk.Toplevel, TranslationMixin):
    """
    View class for exporting comparison result tables to CSV files via a GUI dialog.
    """

    def __init__(self, parent: Any, controller: Any, dfs: List[Any], result_table_labels: List[str], current_tab: int = 0, default_dir: Optional[str] = None) -> None:
        # Initialize parent classes
        tk.Toplevel.__init__(self, parent)
        TranslationMixin.__init__(self)
        
        self.title(self._get_text('export_title'))
        self.grab_set()
        self.resizable(False, False)
        self.controller = controller
        self.dfs = dfs
        self.result_table_labels = result_table_labels
        self.current_tab = current_tab
        self.default_dir = default_dir or os.getcwd()
        self._build_ui()

    def _build_ui(self) -> None:
        """
        Construct and layout the export options UI elements (labels, entries, buttons, listbox, etc.).
        """
        # Label and radio buttons to select which result to export
        tk.Label(self, text=self._get_text('which_result_export')).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.result_var = tk.StringVar(value=str(self.current_tab))
        for i, label in enumerate(self.result_table_labels):
            tk.Radiobutton(self, text=label, variable=self.result_var, value=str(i)).grid(row=0, column=i+1, sticky='w', padx=5, pady=5)
        # Label and listbox to select columns NICHT to export
        tk.Label(self, text=self._get_text('columns_not_export')).grid(row=1, column=0, sticky='nw', padx=10, pady=5)
        self.listbox = tk.Listbox(self, selectmode='multiple', height=8, exportselection=0)
        # Show columns of the current DataFrame in the listbox
        if self.dfs[self.current_tab] is not None:
            for col in self.dfs[self.current_tab].columns:
                self.listbox.insert('end', col)
        self.listbox.grid(row=1, column=1, columnspan=3, sticky='w', padx=5, pady=5)
        self.listbox.config(width=40)
        # Label and entry for export directory
        tk.Label(self, text=self._get_text('target_folder')).grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.path_var = tk.StringVar(value=self.default_dir)
        path_entry = tk.Entry(self, textvariable=self.path_var, width=40)
        path_entry.grid(row=2, column=1, columnspan=2, sticky='w', padx=5, pady=5)
        # Button to open directory chooser dialog
        tk.Button(self, text=self._get_text('choose_folder'), command=self.choose_dir).grid(row=2, column=3, sticky='w', padx=5, pady=5)
        # Label and entry for file name
        tk.Label(self, text=self._get_text('filename_label')).grid(row=3, column=0, sticky='w', padx=10, pady=5)
        default_name = self.result_table_labels[self.current_tab].replace(' ', '_').replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss') + '.csv'
        self.name_var = tk.StringVar(value=default_name)
        name_entry = tk.Entry(self, textvariable=self.name_var, width=30)
        name_entry.grid(row=3, column=1, columnspan=2, sticky='w', padx=5, pady=5)
        # Label and entry for delimiter selection
        tk.Label(self, text=self._get_text('delimiter_label')).grid(row=4, column=0, sticky='w', padx=10, pady=5)
        self.export_delim_var = tk.StringVar(value=';')
        export_delim_entry = tk.Entry(self, textvariable=self.export_delim_var, width=3)
        export_delim_entry.grid(row=4, column=1, sticky='w', padx=5, pady=5)
        # Label and combobox for encoding selection
        tk.Label(self, text=self._get_text('encoding_label')).grid(row=4, column=2, sticky='w', padx=5, pady=5)
        self.export_encoding_var = tk.StringVar(value='latin1')
        export_encoding_combo = ttk.Combobox(self, textvariable=self.export_encoding_var, values=['latin1', 'utf-8', 'cp1252', 'utf-16', 'iso-8859-1'], state='readonly', width=10)
        export_encoding_combo.grid(row=4, column=3, sticky='w', padx=5, pady=5)
        # Button to trigger export
        tk.Button(self, text=self._get_text('export_button'), command=self.do_export).grid(row=5, column=0, columnspan=4, pady=10)
        # Center the dialog on the parent window
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f'+{x}+{y}')

    def choose_dir(self) -> None:
        """
        Open a directory selection dialog to choose the export target folder.
        """
        dir_ = filedialog.askdirectory(initialdir=self.default_dir)
        if dir_:
            self.path_var.set(dir_)

    def do_export(self) -> None:
        """
        Execute the export of the selected result DataFrame to a CSV file, showing success or error messages.
        """
        idx = int(self.result_var.get())
        exclude = [self.listbox.get(i) for i in self.listbox.curselection()]
        out_path = os.path.join(self.path_var.get(), self.name_var.get())
        success, error_msg = self.controller.export_result(
            idx,
            exclude,
            out_path,
            sep=self.export_delim_var.get(),
            encoding=self.export_encoding_var.get()
        )
        if success:
            messagebox.showinfo(self._get_text('export_success_title'), self._get_text('comparison_export_success_message').format(out_path))
            self.destroy()
        else:
            messagebox.showerror(self._get_text('error'), self._get_text('export_error_message').format(error_msg))
