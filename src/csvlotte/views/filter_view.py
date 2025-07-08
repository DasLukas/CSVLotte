"""
Module for FilterView: GUI dialog to apply SQL-like filters to DataFrame and view results.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ..controllers.filter_controller import FilterController
from typing import Any, Callable, Optional

class FilterView(tk.Toplevel):
    """
    View class for filtering a DataFrame: shows data in a table, allows filter input, and updates view.
    """
    def __init__(self, parent: Any, df: Any, var: Any, title: str, apply_callback: Optional[Callable[[str], None]] = None, source_path: Optional[str] = None) -> None:
        """
        Initialize the filter dialog with DataFrame and callback for applying filters.

        Args:
            parent (Any): Parent GUI window.
            df (Any): DataFrame to filter.
            var (Any): Tkinter variable for filter string.
            title (str): Window title.
            apply_callback (Optional[Callable[[str], None]]): Callback after filter applied.
            source_path (Optional[str]): Original file path for export.
        """
        super().__init__(parent)
        self.title(title)
        self.grab_set()
        self.resizable(True, True)
        self.var = var
        self.apply_callback = apply_callback
        self.controller = FilterController(df)
        self.source_path = source_path
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        width = int(screen_w * 2 / 3)
        height = int(screen_h * 2 / 3)
        x = (screen_w // 2) - (width // 2)
        y = (screen_h // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self._build_ui()

    def _build_ui(self) -> None:
        # Table frame at the top (contains the data table and scrollbars)
        table_frame = tk.Frame(self)
        table_frame.pack(fill='both', expand=True, side='top', padx=10, pady=(10, 2))
        # Treeview widget for displaying the DataFrame as a table
        self.tree = ttk.Treeview(table_frame, show='headings')
        self.tree.grid(row=0, column=0, sticky='nsew')
        # Show all columns in the table
        self.tree['displaycolumns'] = '#all'
        # Vertical scrollbar for the table
        yscroll = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        yscroll.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=yscroll.set)
        # Horizontal scrollbar for the table
        xscroll = ttk.Scrollbar(table_frame, orient='horizontal', command=self.tree.xview)
        xscroll.grid(row=1, column=0, sticky='ew')
        self.tree.configure(xscrollcommand=xscroll.set)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # Label for row count (between table and filter input)
        self.rowcount_var = tk.StringVar()
        self.rowcount_label = tk.Label(self, textvariable=self.rowcount_var, anchor='w')
        self.rowcount_label.pack(fill='x', padx=10, pady=(0, 2))

        # Bottom frame contains filter input and action buttons
        bottom_frame = tk.Frame(self)
        bottom_frame.pack(side='bottom', fill='x', padx=10, pady=10)
        # Label for the filter input
        tk.Label(bottom_frame, text='Filter:').pack(side='left', padx=(0, 5))
        # Text widget for entering the filter string
        self.text = tk.Text(bottom_frame, height=1)
        self.text.pack(side='left', padx=(0, 5), fill='x', expand=True)
        self.text.insert('1.0', self.var.get())

        # Bind Enter key to apply the filter
        self.text.bind('<Return>', self._on_enter)

        # Frame for action buttons (Apply, Export, Close)
        btn_frame = tk.Frame(bottom_frame)
        btn_frame.pack(side='left', padx=5)
        # Button to apply the filter and update the table
        tk.Button(btn_frame, text='Übernehmen', command=self._apply_and_update).pack(side='left', padx=5)
        # Button to export the filtered data
        tk.Button(btn_frame, text='Exportieren', command=self._export_filtered).pack(side='left', padx=5)
        # Button to close the dialog
        tk.Button(btn_frame, text='Schließen', command=self.destroy).pack(side='left', padx=5)

        # Initially populate the table with data (must be last!)
        self._populate_table()

    def _on_enter(self) -> None:
        self._apply_and_update()

    def _populate_table(self) -> None:
        df = self.controller.get_filtered()
        self.tree.delete(*self.tree.get_children())
        self._sort_state = getattr(self, '_sort_state', {})
        # Update row count label
        if df is not None and not df.empty:
            self.rowcount_var.set(f"Gefundene Zeilen: {len(df)}")
            cols = list(df.columns)
            self.tree['columns'] = cols
            for col in cols:
                arrow = ''
                if col in self._sort_state:
                    arrow = ' ▲' if self._sort_state[col] else ' ▼'
                self.tree.heading(col, text=col + arrow, command=lambda c=col: self._sort_by_column(c, False))
                maxlen = max([len(str(val)) for val in df[col]] + [len(str(col))])
                width = min(max(80, maxlen * 8), 300)
                self.tree.column(col, width=width, minwidth=80, stretch=False)
            for _, row in df.iterrows():
                self.tree.insert('', 'end', values=list(row))
        else:
            self.rowcount_var.set("Gefundene Zeilen: 0")
            self.tree['columns'] = []

    def _sort_by_column(self, col: str, reverse: bool) -> None:
        df = self.controller.get_filtered()
        if df is None or df.empty:
            return
        try:
            sorted_df = df.sort_values(by=col, ascending=not reverse)
        except Exception:
            return
        self.tree.delete(*self.tree.get_children())
        for _, row in sorted_df.iterrows():
            self.tree.insert('', 'end', values=list(row))
        if not hasattr(self, '_sort_state'):
            self._sort_state = {}
        self._sort_state = {c: None for c in df.columns}
        self._sort_state[col] = not reverse
        for c in df.columns:
            arrow = ''
            if c == col:
                arrow = ' ▲' if not reverse else ' ▼'
            self.tree.heading(c, text=c + arrow, command=lambda cc=c: self._sort_by_column(cc, False if cc != col else not reverse))

    def _apply_and_update(self) -> None:
        filter_str = self.text.get('1.0', 'end').strip()
        self.var.set(filter_str)
        df_filtered = self.controller.apply_filter(filter_str)
        if df_filtered is None:
            messagebox.showerror('Fehler', 'Filter konnte nicht angewendet werden. Bitte prüfen Sie die Syntax.')
            return
        self._populate_table()
        if self.apply_callback:
            self.apply_callback(filter_str)

    def _export_filtered(self) -> None:
        from csvlotte.controllers.filter_export_controller import FilterExportController
        df = self.controller.get_filtered()
        if df is None or df.empty:
            messagebox.showerror('Fehler', 'Keine Daten zum Exportieren!')
            return
        source_path = self.source_path
        if not source_path:
            if hasattr(self.master, 'df1') and self.master.df1 is not None and self.controller.df is self.master.df1:
                source_path = getattr(self.master, 'file1_path', None)
            elif hasattr(self.master, 'df2') and self.master.df2 is not None and self.controller.df is self.master.df2:
                source_path = getattr(self.master, 'file2_path', None)
            if not source_path and hasattr(self.master, 'file1_path'):
                source_path = getattr(self.master, 'file1_path', None)
        FilterExportController(self, df, source_path=source_path).open_export_dialog()
