"""
Module for HomeView: renders the main GUI, displays CSV data, and integrates filtering/comparison views.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

class HomeView:
    """
    View class responsible for displaying CSV data, filter dialogs, and comparison results.
    """

    def __init__(self, root: Any, controller: Any) -> None:
        """
        Initialize the HomeView with the root window and controller.
        """
        self.root = root
        self.controller = controller
        self.root.title('CSVLotte - CSV Comparison Tool')
        self.root.geometry('900x500')
        self.root.resizable(True, True)
        self.file1_path = ''
        self.file2_path = ''
        self.df1 = None
        self.df2 = None

        self._set_window_icon()

        self._create_widgets()

    def _set_window_icon(self):
        """
        Set the window icon depending on the platform.
        """
        try:
            import os, sys
            base_dir = os.path.dirname(__file__)
            assets_dir = os.path.abspath(os.path.join(base_dir, '..', 'assets'))
            icon_img = None
            if sys.platform.startswith('win'):
                ico_path = os.path.join(assets_dir, 'logo.ico')
                if os.path.exists(ico_path):
                    self.root.iconbitmap(ico_path)
                else:
                    png_path = os.path.join(assets_dir, 'logo.png')
                    if os.path.exists(png_path):
                        icon_img = tk.PhotoImage(file=png_path)
                        self.root.iconphoto(True, icon_img)
            elif sys.platform == 'darwin':
                png_path = os.path.join(assets_dir, 'logo.png')
                if os.path.exists(png_path):
                    icon_img = tk.PhotoImage(file=png_path)
                    self.root.iconphoto(True, icon_img)
            else:
                png_path = os.path.join(assets_dir, 'logo.png')
                if os.path.exists(png_path):
                    icon_img = tk.PhotoImage(file=png_path)
                    self.root.iconphoto(True, icon_img)
            if icon_img is not None:
                self._logo_img = icon_img
        except Exception as e:
            print(f'Konnte Icon nicht setzen: {e}')

    def _create_widgets(self) -> None:
        """
        Build and layout all GUI widgets for file selection, filters, and result display.
        """
        # Progress bar at the bottom of the window, always visible
        self.progress = ttk.Progressbar(self.root, orient='horizontal', mode='determinate')
        self.progress.pack(side='bottom', fill='x', padx=10, pady=(0,10))
        style = ttk.Style(self.root)
        style.theme_use('default')
        style.configure("green.Horizontal.TProgressbar", foreground='green', background='green')
        self.progress.configure(style="green.Horizontal.TProgressbar")

        # Top control panel: vertical stack, left-aligned
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(anchor='w', padx=10, pady=10, fill='x')

        # --- File selection row for CSV 1 ---
        file_row1 = tk.Frame(self.control_frame)
        file_row1.pack(anchor='w', fill='x')
        # Button to select CSV 1
        tk.Button(file_row1, text='CSV 1 auswählen', command=self.controller.load_file1).pack(side='left', padx=5, pady=5)
        # Label showing selected file name for CSV 1
        self.file1_label = tk.Label(file_row1, text='Keine Datei gewählt')
        self.file1_label.pack(side='left', padx=5, pady=5)
        # Delimiter label and entry for CSV 1
        tk.Label(file_row1, text='Trennz.:').pack(side='left', padx=(10,0), pady=5)
        self.delim_var1 = tk.StringVar(value=';')
        self.delim_entry1 = tk.Entry(file_row1, textvariable=self.delim_var1, width=3)
        self.delim_entry1.pack(side='left', padx=2, pady=5)
        # Encoding label and combobox for CSV 1
        tk.Label(file_row1, text='Enc.').pack(side='left', padx=(5,0), pady=5)
        self.encoding_var1 = tk.StringVar(value='latin1')
        encodings = ['latin1', 'utf-8', 'cp1252', 'utf-16', 'iso-8859-1']
        self.encoding_combo1 = ttk.Combobox(file_row1, textvariable=self.encoding_var1, values=encodings, state='readonly', width=10)
        self.encoding_combo1.pack(side='left', padx=2, pady=5)
        # Reload and info buttons for CSV 1
        self.delim_var1.trace_add('write', lambda *args: self.controller.reload_file1() if self.file1_path else None)
        self.encoding_var1.trace_add('write', lambda *args: self.controller.reload_file1() if self.file1_path else None)
        self.file1_reload_btn = tk.Button(file_row1, text='⟳', command=self.controller.reload_file1, state='disabled', width=2)
        self.file1_reload_btn.pack(side='left', padx=(2,0), pady=5)
        self.file1_info_btn = tk.Button(file_row1, text='ℹ️', command=lambda: self.controller.show_file_info(1), state='disabled', width=2)
        self.file1_info_btn.pack(side='left', padx=2, pady=5)

        # --- Filter row for CSV 1 ---
        filter_row1 = tk.Frame(self.control_frame)
        filter_row1.pack(anchor='w', fill='x', padx=5, pady=(0,2))
        # Label and entry for SQL WHERE filter for CSV 1
        tk.Label(filter_row1, text='Filter (WHERE SQL):').pack(side='left', padx=(0,2), pady=2)
        self.filter1_var = tk.StringVar()
        self.filter1_entry = tk.Entry(filter_row1, textvariable=self.filter1_var, width=50)
        self.filter1_entry.pack(side='left', padx=2, pady=2)
        # Button to open filter dialog for CSV 1
        self.filter1_btn = tk.Button(filter_row1, text='...', width=2, command=lambda: self.open_filter_window(1), state='disabled')
        self.filter1_btn.pack(side='left', padx=(2,0), pady=2)

        # --- File selection row for CSV 2 ---
        file_row2 = tk.Frame(self.control_frame)
        file_row2.pack(anchor='w', fill='x')
        # Button to select CSV 2
        tk.Button(file_row2, text='CSV 2 auswählen', command=self.controller.load_file2).pack(side='left', padx=5, pady=5)
        # Label showing selected file name for CSV 2
        self.file2_label = tk.Label(file_row2, text='Keine Datei gewählt')
        self.file2_label.pack(side='left', padx=5, pady=5)
        # Delimiter label and entry for CSV 2
        tk.Label(file_row2, text='Trennz.:').pack(side='left', padx=(10,0), pady=5)
        self.delim_var2 = tk.StringVar(value=';')
        self.delim_entry2 = tk.Entry(file_row2, textvariable=self.delim_var2, width=3)
        self.delim_entry2.pack(side='left', padx=2, pady=5)
        # Encoding label and combobox for CSV 2
        tk.Label(file_row2, text='Enc.').pack(side='left', padx=(5,0), pady=5)
        self.encoding_var2 = tk.StringVar(value='latin1')
        self.encoding_combo2 = ttk.Combobox(file_row2, textvariable=self.encoding_var2, values=encodings, state='readonly', width=10)
        self.encoding_combo2.pack(side='left', padx=2, pady=5)
        # Reload and info buttons for CSV 2
        self.delim_var2.trace_add('write', lambda *args: self.controller.reload_file2() if self.file2_path else None)
        self.encoding_var2.trace_add('write', lambda *args: self.controller.reload_file2() if self.file2_path else None)
        self.file2_reload_btn = tk.Button(file_row2, text='⟳', command=self.controller.reload_file2, state='disabled', width=2)
        self.file2_reload_btn.pack(side='left', padx=(2,0), pady=5)
        self.file2_info_btn = tk.Button(file_row2, text='ℹ️', command=lambda: self.controller.show_file_info(2), state='disabled', width=2)
        self.file2_info_btn.pack(side='left', padx=2, pady=5)

        # --- Filter row for CSV 2 ---
        filter_row2 = tk.Frame(self.control_frame)
        filter_row2.pack(anchor='w', fill='x', padx=5, pady=(0,2))
        # Label and entry for SQL WHERE filter for CSV 2
        tk.Label(filter_row2, text='Filter (WHERE SQL):').pack(side='left', padx=(0,2), pady=2)
        self.filter2_var = tk.StringVar()
        self.filter2_entry = tk.Entry(filter_row2, textvariable=self.filter2_var, width=50)
        self.filter2_entry.pack(side='left', padx=2, pady=2)
        # Button to open filter dialog for CSV 2
        self.filter2_btn = tk.Button(filter_row2, text='...', width=2, command=lambda: self.open_filter_window(2), state='disabled')
        self.filter2_btn.pack(side='left', padx=(2,0), pady=2)

        # --- Comparison columns and slice entries ---
        col_frame = tk.Frame(self.control_frame)
        col_frame.pack(anchor='w', fill='x')
        # Row for comparison column and slice for CSV 1
        row_col1 = tk.Frame(col_frame)
        row_col1.pack(anchor='w', fill='x')
        tk.Label(row_col1, text='Vergleichsspalte CSV 1:').pack(side='left', padx=5, pady=5)
        self.column_combo1 = ttk.Combobox(row_col1, state='readonly')
        self.column_combo1.pack(side='left', padx=5, pady=5)
        tk.Label(row_col1, text='Slice:').pack(side='left', padx=(10,2), pady=5)
        self.col1_text_var = tk.StringVar()
        self.col1_text_entry = tk.Entry(row_col1, textvariable=self.col1_text_var, width=7)
        self.col1_text_entry.pack(side='left', padx=2, pady=5)
        # Row for comparison column and slice for CSV 2
        row_col2 = tk.Frame(col_frame)
        row_col2.pack(anchor='w', fill='x')
        tk.Label(row_col2, text='Vergleichsspalte CSV 2:').pack(side='left', padx=5, pady=5)
        self.column_combo2 = ttk.Combobox(row_col2, state='readonly')
        self.column_combo2.pack(side='left', padx=5, pady=5)
        tk.Label(row_col2, text='Slice:').pack(side='left', padx=(10,2), pady=5)
        self.col2_text_var = tk.StringVar()
        self.col2_text_entry = tk.Entry(row_col2, textvariable=self.col2_text_var, width=7)
        self.col2_text_entry.pack(side='left', padx=2, pady=5)

        # --- Compare and export buttons ---
        row5 = tk.Frame(self.control_frame)
        row5.pack(anchor='w', fill='x')
        # Button to start comparison
        self.compare_btn = tk.Button(row5, text='Vergleichen', command=self.controller.compare_csvs, state='disabled')
        self.compare_btn.pack(side='left', padx=5, pady=10)
        # Button to export comparison results
        self.export_btn = tk.Button(row5, text='Vergleich exportieren', command=self.controller.export_results_button, state='disabled')
        self.export_btn.pack(side='left', padx=5, pady=10)

        # --- Result display: notebook with tabs for result tables ---
        result_frame = tk.Frame(self.root)
        result_frame.pack(padx=10, pady=10, fill='both', expand=True)
        result_frame.rowconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)
        # Tab labels with dynamic file names
        file1_name = self.file1_path.split("\\")[-1] if self.file1_path else "CSV1"
        file2_name = self.file2_path.split("\\")[-1] if self.file2_path else "CSV2"
        self.result_table_labels = [
            f'Nur in {file1_name}',
            f'Gemeinsame in {file1_name}',
            f'Gemeinsame in {file2_name}',
            f'Nur in {file2_name}'
        ]
        # Notebook widget for result tables
        self.notebook = ttk.Notebook(result_frame)
        self.notebook.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)
        self.result_table_frames = []
        self.result_tables = []
        self._result_dfs = [None, None, None, None]
        self._tab_ids = []
        for label in self.result_table_labels:
            # Each tab contains a frame with a Treeview (table) and scrollbars
            tab_frame = tk.Frame(self.notebook)
            tab_frame.rowconfigure(0, weight=1)
            tab_frame.columnconfigure(0, weight=1)
            tree = ttk.Treeview(tab_frame, show='headings')
            tree.grid(row=0, column=0, sticky='nsew')
            xscroll = ttk.Scrollbar(tab_frame, orient='horizontal', command=tree.xview)
            xscroll.grid(row=1, column=0, sticky='ew')
            tree.configure(xscrollcommand=xscroll.set)
            yscroll = ttk.Scrollbar(tab_frame, orient='vertical', command=tree.yview)
            yscroll.grid(row=0, column=1, sticky='ns')
            tree.configure(yscrollcommand=yscroll.set)
            tab_id = self.notebook.add(tab_frame, text=label, state='disabled')
            tab_frame.pack_propagate(False)
            tab_frame.grid_propagate(True)
            self.result_table_frames.append(tab_frame)
            self.result_tables.append(tree)
            self._tab_ids.append(tab_frame)

    def update_result_table_view(self) -> None:
        """
        Refresh the result tables based on current DataFrame results.
        """
        if not hasattr(self, '_sort_states'):
            self._sort_states = [{} for _ in self.result_tables]
        for idx, tree in enumerate(self.result_tables):
            tree.delete(*tree.get_children())
            df = self._result_dfs[idx] if self._result_dfs and len(self._result_dfs) > idx else None
            sort_state = self._sort_states[idx] if hasattr(self, '_sort_states') else {}
            tree['displaycolumns'] = '#all'
            if df is not None and not df.empty:
                cols = list(df.columns)
                tree['columns'] = cols
                for col in cols:
                    arrow = ''
                    if col in sort_state:
                        arrow = ' ▲' if sort_state[col] else ' ▼'
                    tree.heading(col, text=col + arrow, command=lambda c=col, t=tree, i=idx: self._sort_result_column(i, t, c, False))
                    maxlen = max([len(str(val)) for val in df[col]] + [len(str(col))])
                    width = min(max(80, maxlen * 8), 300)
                    tree.column(col, width=width, minwidth=80, stretch=False)
                for _, row in df.iterrows():
                    tree.insert('', 'end', values=list(row))
            else:
                tree['columns'] = []

    def _sort_result_column(self, idx: int, tree: Any, col: str, reverse: bool) -> None:
        """
        Sort a result table column in ascending or descending order.
        """
        df = self._result_dfs[idx]
        if df is None or df.empty:
            return
        try:
            sorted_df = df.sort_values(by=col, ascending=not reverse)
        except Exception:
            return
        tree.delete(*tree.get_children())
        for _, row in sorted_df.iterrows():
            tree.insert('', 'end', values=list(row))
        if not hasattr(self, '_sort_states'):
            self._sort_states = [{} for _ in self.result_tables]
        self._sort_states[idx] = {c: None for c in df.columns}
        self._sort_states[idx][col] = not reverse
        for c in df.columns:
            arrow = ''
            if c == col:
                arrow = ' ▲' if not reverse else ' ▼'
            tree.heading(c, text=c + arrow, command=lambda cc=c, t=tree, i=idx: self._sort_result_column(i, t, cc, False if cc != col else not reverse))
    
    def open_filter_window(self, csv_num: int) -> None:
        """
        Open the filter dialog for CSV 1 or CSV 2 and apply user-defined filters.
        :param csv_num: 1 for CSV 1, 2 for CSV 2
        """
        if csv_num == 1:
            df = self.df1
            filter_var = self.filter1_var
            file_path = self.file1_path
            title = 'Filter für CSV 1'
        else:
            df = self.df2
            filter_var = self.filter2_var
            file_path = self.file2_path
            title = 'Filter für CSV 2'
        if df is None:
            messagebox.showwarning('Hinweis', f'Bitte zuerst eine Datei für CSV {csv_num} laden.')
            return
        from .filter_view import FilterView
        def on_apply(filter_str):
            from ..controllers.filter_controller import FilterController
            fc = FilterController(df)
            filtered = fc.apply_filter(filter_str)
            if filtered is not None:
                if csv_num == 1:
                    self.df1 = filtered
                else:
                    self.df2 = filtered
                self.controller.update_columns()
                self.controller.enable_compare_btn()
        FilterView(self.root, df, filter_var, title, apply_callback=on_apply, source_path=file_path)

    def sync_column_selection(self) -> None:
        """
        Synchronize the selected column between CSV 1 and CSV 2 selectors.
        """
        selected_col1 = self.column_combo1.get()
        if self.df2 is not None and selected_col1:
            if selected_col1 in self.df2.columns:
                self.column_combo2.set(selected_col1)
    
    def update_filter_buttons(self):
        if self.df1 is not None:
            self.filter1_btn.config(state='normal')
        else:
            self.filter1_btn.config(state='disabled')
        if self.df2 is not None:
            self.filter2_btn.config(state='normal')
        else:
            self.filter2_btn.config(state='disabled')