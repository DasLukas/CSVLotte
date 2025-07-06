"""
Module for CompareExportView: GUI dialog to configure and export comparison results to CSV files.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Any, List, Optional
import os

class CompareExportView(tk.Toplevel):
    """
    View class for exporting comparison result tables to CSV files via a GUI dialog.
    """

    def __init__(self, parent: Any, controller: Any, dfs: List[Any], result_table_labels: List[str], current_tab: int = 0, default_dir: Optional[str] = None) -> None:
        super().__init__(parent)
        self.title('Exportieren')
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
        tk.Label(self, text='Welches Ergebnis exportieren?').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.result_var = tk.StringVar(value=str(self.current_tab))
        for i, label in enumerate(self.result_table_labels):
            tk.Radiobutton(self, text=label, variable=self.result_var, value=str(i)).grid(row=0, column=i+1, sticky='w', padx=5, pady=5)
        tk.Label(self, text='Spalten NICHT exportieren:').grid(row=1, column=0, sticky='nw', padx=10, pady=5)
        self.listbox = tk.Listbox(self, selectmode='multiple', height=8, exportselection=0)
        # Zeige Spalten des aktuellen DataFrames an
        if self.dfs[self.current_tab] is not None:
            for col in self.dfs[self.current_tab].columns:
                self.listbox.insert('end', col)
        self.listbox.grid(row=1, column=1, columnspan=3, sticky='w', padx=5, pady=5)
        self.listbox.config(width=40)
        tk.Label(self, text='Zielordner:').grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.path_var = tk.StringVar(value=self.default_dir)
        path_entry = tk.Entry(self, textvariable=self.path_var, width=40)
        path_entry.grid(row=2, column=1, columnspan=2, sticky='w', padx=5, pady=5)
        tk.Button(self, text='Ordner wählen...', command=self.choose_dir).grid(row=2, column=3, sticky='w', padx=5, pady=5)
        tk.Label(self, text='Dateiname:').grid(row=3, column=0, sticky='w', padx=10, pady=5)
        default_name = self.result_table_labels[self.current_tab].replace(' ', '_').replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss') + '.csv'
        self.name_var = tk.StringVar(value=default_name)
        name_entry = tk.Entry(self, textvariable=self.name_var, width=30)
        name_entry.grid(row=3, column=1, columnspan=2, sticky='w', padx=5, pady=5)
        tk.Label(self, text='Trennzeichen:').grid(row=4, column=0, sticky='w', padx=10, pady=5)
        self.export_delim_var = tk.StringVar(value=';')
        export_delim_entry = tk.Entry(self, textvariable=self.export_delim_var, width=3)
        export_delim_entry.grid(row=4, column=1, sticky='w', padx=5, pady=5)
        tk.Label(self, text='Encoding:').grid(row=4, column=2, sticky='w', padx=5, pady=5)
        self.export_encoding_var = tk.StringVar(value='latin1')
        export_encoding_combo = ttk.Combobox(self, textvariable=self.export_encoding_var, values=['latin1', 'utf-8', 'cp1252', 'utf-16', 'iso-8859-1'], state='readonly', width=10)
        export_encoding_combo.grid(row=4, column=3, sticky='w', padx=5, pady=5)
        tk.Button(self, text='Exportieren', command=self.do_export).grid(row=5, column=0, columnspan=4, pady=10)
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
            messagebox.showinfo('Export', f'Ergebnis wurde gespeichert: {out_path}')
            self.destroy()
        else:
            messagebox.showerror('Fehler', f'Export fehlgeschlagen:\n{error_msg}')
