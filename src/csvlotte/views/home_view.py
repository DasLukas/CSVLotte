import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd

class HomeView:

    def update_result_table_view(self, event=None):
        # Aktualisiert alle Ergebnis-Tabs entsprechend der vom Controller gelieferten DataFrames
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
                    # Spaltenbreite nach Inhalt setzen (max 300px, min 80px)
                    maxlen = max([len(str(val)) for val in df[col]] + [len(str(col))])
                    width = min(max(80, maxlen * 8), 300)
                    tree.column(col, width=width, minwidth=80, stretch=False)
                for _, row in df.iterrows():
                    tree.insert('', 'end', values=list(row))
            else:
                tree['columns'] = []

    def _sort_result_column(self, idx, tree, col, reverse):
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
        # Sortierstatus aktualisieren
        if not hasattr(self, '_sort_states'):
            self._sort_states = [{} for _ in self.result_tables]
        self._sort_states[idx] = {c: None for c in df.columns}
        self._sort_states[idx][col] = not reverse
        for c in df.columns:
            arrow = ''
            if c == col:
                arrow = ' ▲' if not reverse else ' ▼'
            tree.heading(c, text=c + arrow, command=lambda cc=c, t=tree, i=idx: self._sort_result_column(i, t, cc, False if cc != col else not reverse))
    def open_filter1_window(self):
        if self.df1 is None:
            messagebox.showwarning('Hinweis', 'Bitte zuerst eine Datei für CSV 1 laden.')
            return
        from .filter_view import FilterView
        def on_apply(filter_str):
            from ..controllers.filter_controller import FilterController
            fc = FilterController(self.df1)
            filtered = fc.apply_filter(filter_str)
            if filtered is not None:
                self.df1 = filtered
                self.controller.update_columns()
                self.controller.enable_compare_btn()
        FilterView(self.root, self.df1, self.filter1_var, 'Filter für CSV 1', apply_callback=on_apply, source_path=self.file1_path)

    def open_filter2_window(self):
        if self.df2 is None:
            messagebox.showwarning('Hinweis', 'Bitte zuerst eine Datei für CSV 2 laden.')
            return
        from .filter_view import FilterView
        def on_apply(filter_str):
            from ..controllers.filter_controller import FilterController
            fc = FilterController(self.df2)
            filtered = fc.apply_filter(filter_str)
            if filtered is not None:
                self.df2 = filtered
                self.controller.update_columns()
                self.controller.enable_compare_btn()
        FilterView(self.root, self.df2, self.filter2_var, 'Filter für CSV 2', apply_callback=on_apply, source_path=self.file2_path)
    def sync_column_selection(self, event=None):
        # Synchronisiert die Auswahl der Vergleichsspalte 1 auf Vergleichsspalte 2, falls vorhanden
        selected_col1 = self.column_combo1.get()
        if self.df2 is not None and selected_col1:
            if selected_col1 in self.df2.columns:
                self.column_combo2.set(selected_col1)
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title('CSVLotte')
        self.root.geometry('900x500')
        self.root.resizable(True, True)
        self.file1_path = ''
        self.file2_path = ''
        self.df1 = None
        self.df2 = None

        # Fortschrittsbalken unter der Ergebnistabelle, volle Breite (immer sichtbar)
        self.progress = ttk.Progressbar(self.root, orient='horizontal', mode='determinate')
        self.progress.pack(side='bottom', fill='x', padx=10, pady=(0,10))
        style = ttk.Style(self.root)
        style.theme_use('default')
        style.configure("green.Horizontal.TProgressbar", foreground='green', background='green')
        self.progress.configure(style="green.Horizontal.TProgressbar")

        # Fenster-Icon setzen (automatische Auswahl je nach Plattform)
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
                self._logo_img = icon_img  # Referenz halten
        except Exception as e:
            print(f'Konnte Icon nicht setzen: {e}')

        self.create_widgets()

    def create_widgets(self):
        # Oberes Bedienfeld: alles linksbündig in einer vertikalen Spalte
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(anchor='w', padx=10, pady=10, fill='x')

        # File selectors
        file_row1 = tk.Frame(self.control_frame)
        file_row1.pack(anchor='w', fill='x')
        tk.Button(file_row1, text='CSV 1 auswählen', command=self.controller.load_file1).pack(side='left', padx=5, pady=5)
        self.file1_label = tk.Label(file_row1, text='Keine Datei gewählt')
        self.file1_label.pack(side='left', padx=5, pady=5)
        tk.Label(file_row1, text='Trennz.:').pack(side='left', padx=(10,0), pady=5)
        self.delim_var1 = tk.StringVar(value=';')
        self.delim_entry1 = tk.Entry(file_row1, textvariable=self.delim_var1, width=3)
        self.delim_entry1.pack(side='left', padx=2, pady=5)
        tk.Label(file_row1, text='Enc.').pack(side='left', padx=(5,0), pady=5)
        self.encoding_var1 = tk.StringVar(value='latin1')
        encodings = ['latin1', 'utf-8', 'cp1252', 'utf-16', 'iso-8859-1']
        self.encoding_combo1 = ttk.Combobox(file_row1, textvariable=self.encoding_var1, values=encodings, state='readonly', width=10)
        self.encoding_combo1.pack(side='left', padx=2, pady=5)
        self.delim_var1.trace_add('write', lambda *args: self.controller.reload_file1() if self.file1_path else None)
        self.encoding_var1.trace_add('write', lambda *args: self.controller.reload_file1() if self.file1_path else None)
        self.file1_reload_btn = tk.Button(file_row1, text='⟳', command=self.controller.reload_file1, state='disabled', width=2)
        self.file1_reload_btn.pack(side='left', padx=(2,0), pady=5)
        self.file1_info_btn = tk.Button(file_row1, text='ℹ️', command=self.controller.show_file1_info, state='disabled', width=2)
        self.file1_info_btn.pack(side='left', padx=2, pady=5)

        # WHERE-Filter für CSV 1
        filter_row1 = tk.Frame(self.control_frame)
        filter_row1.pack(anchor='w', fill='x', padx=5, pady=(0,2))
        tk.Label(filter_row1, text='Filter (WHERE SQL):').pack(side='left', padx=(0,2), pady=2)
        self.filter1_var = tk.StringVar()
        self.filter1_entry = tk.Entry(filter_row1, textvariable=self.filter1_var, width=50)
        self.filter1_entry.pack(side='left', padx=2, pady=2)
        self.filter1_btn = tk.Button(filter_row1, text='...', width=2, command=self.controller.open_filter1_window, state='disabled')
        self.filter1_btn.pack(side='left', padx=(2,0), pady=2)

        file_row2 = tk.Frame(self.control_frame)
        file_row2.pack(anchor='w', fill='x')
        tk.Button(file_row2, text='CSV 2 auswählen', command=self.controller.load_file2).pack(side='left', padx=5, pady=5)
        self.file2_label = tk.Label(file_row2, text='Keine Datei gewählt')
        self.file2_label.pack(side='left', padx=5, pady=5)
        tk.Label(file_row2, text='Trennz.:').pack(side='left', padx=(10,0), pady=5)
        self.delim_var2 = tk.StringVar(value=';')
        self.delim_entry2 = tk.Entry(file_row2, textvariable=self.delim_var2, width=3)
        self.delim_entry2.pack(side='left', padx=2, pady=5)
        tk.Label(file_row2, text='Enc.').pack(side='left', padx=(5,0), pady=5)
        self.encoding_var2 = tk.StringVar(value='latin1')
        self.encoding_combo2 = ttk.Combobox(file_row2, textvariable=self.encoding_var2, values=encodings, state='readonly', width=10)
        self.encoding_combo2.pack(side='left', padx=2, pady=5)
        self.delim_var2.trace_add('write', lambda *args: self.controller.reload_file2() if self.file2_path else None)
        self.encoding_var2.trace_add('write', lambda *args: self.controller.reload_file2() if self.file2_path else None)
        self.file2_reload_btn = tk.Button(file_row2, text='⟳', command=self.controller.reload_file2, state='disabled', width=2)
        self.file2_reload_btn.pack(side='left', padx=(2,0), pady=5)
        self.file2_info_btn = tk.Button(file_row2, text='ℹ️', command=self.controller.show_file2_info, state='disabled', width=2)
        self.file2_info_btn.pack(side='left', padx=2, pady=5)

        # WHERE-Filter für CSV 2 (jetzt direkt unter Dateiauswahl)
        filter_row2 = tk.Frame(self.control_frame)
        filter_row2.pack(anchor='w', fill='x', padx=5, pady=(0,2))
        tk.Label(filter_row2, text='Filter (WHERE SQL):').pack(side='left', padx=(0,2), pady=2)
        self.filter2_var = tk.StringVar()
        self.filter2_entry = tk.Entry(filter_row2, textvariable=self.filter2_var, width=50)
        self.filter2_entry.pack(side='left', padx=2, pady=2)
        self.filter2_btn = tk.Button(filter_row2, text='...', width=2, command=self.controller.open_filter2_window, state='disabled')
        self.filter2_btn.pack(side='left', padx=(2,0), pady=2)

        # Vergleichsspalten und Slices
        col_frame = tk.Frame(self.control_frame)
        col_frame.pack(anchor='w', fill='x')
        # Column 1
        row_col1 = tk.Frame(col_frame)
        row_col1.pack(anchor='w', fill='x')
        tk.Label(row_col1, text='Vergleichsspalte CSV 1:').pack(side='left', padx=5, pady=5)
        self.column_combo1 = ttk.Combobox(row_col1, state='readonly')
        self.column_combo1.pack(side='left', padx=5, pady=5)
        tk.Label(row_col1, text='Slice:').pack(side='left', padx=(10,2), pady=5)
        self.col1_text_var = tk.StringVar()
        self.col1_text_entry = tk.Entry(row_col1, textvariable=self.col1_text_var, width=7)
        self.col1_text_entry.pack(side='left', padx=2, pady=5)
        # Column 2
        row_col2 = tk.Frame(col_frame)
        row_col2.pack(anchor='w', fill='x')
        tk.Label(row_col2, text='Vergleichsspalte CSV 2:').pack(side='left', padx=5, pady=5)
        self.column_combo2 = ttk.Combobox(row_col2, state='readonly')
        self.column_combo2.pack(side='left', padx=5, pady=5)
        tk.Label(row_col2, text='Slice:').pack(side='left', padx=(10,2), pady=5)
        self.col2_text_var = tk.StringVar()
        self.col2_text_entry = tk.Entry(row_col2, textvariable=self.col2_text_var, width=7)
        self.col2_text_entry.pack(side='left', padx=2, pady=5)

        # Vergleichsbutton und Exportbutton
        row5 = tk.Frame(self.control_frame)
        row5.pack(anchor='w', fill='x')
        self.compare_btn = tk.Button(row5, text='Vergleichen', command=self.controller.compare_csvs, state='disabled')
        self.compare_btn.pack(side='left', padx=5, pady=10)
        self.export_btn = tk.Button(row5, text='Vergleich exportieren', command=self.controller.export_results_button, state='disabled')
        self.export_btn.pack(side='left', padx=5, pady=10)

        # Ergebnisanzeige: Eine Tabelle über die gesamte Breite, mit Dropdown zur Auswahl
        result_frame = tk.Frame(self.root)
        result_frame.pack(padx=10, pady=10, fill='both', expand=True)
        result_frame.rowconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)
        # Dynamische Tab-Benennung mit Dateinamen
        file1_name = self.file1_path.split("\\")[-1] if self.file1_path else "CSV1"
        file2_name = self.file2_path.split("\\")[-1] if self.file2_path else "CSV2"
        self.result_table_labels = [
            f'Nur in {file1_name}',
            f'Gemeinsame in {file1_name}',
            f'Gemeinsame in {file2_name}',
            f'Nur in {file2_name}'
        ]
        self.notebook = ttk.Notebook(result_frame)
        self.notebook.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)
        self.result_table_frames = []
        self.result_tables = []
        self._result_dfs = [None, None, None, None]
        self._tab_ids = []
        for label in self.result_table_labels:
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

    def update_filter_buttons(self):
        # Aktiviert die Filter-Buttons nur, wenn eine Datei geladen ist
        if self.df1 is not None:
            self.filter1_btn.config(state='normal')
        else:
            self.filter1_btn.config(state='disabled')
        if self.df2 is not None:
            self.filter2_btn.config(state='normal')
        else:
            self.filter2_btn.config(state='disabled')

    # Nach dem Laden/Reload einer Datei update_filter_buttons aufrufen
    # Das sollte in den Callbacks nach dem Laden/Filtern passieren:
    # self.update_filter_buttons()