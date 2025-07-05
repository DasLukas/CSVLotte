import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd

class CSVLotteApp:
    def _treeview_sort_column(self, tree, col, reverse):
        # Sortiere die Werte in der Spalte col
        data = [(tree.set(k, col), k) for k in tree.get_children('')]
        try:
            data.sort(key=lambda t: float(t[0].replace(',', '.')), reverse=reverse)
        except Exception:
            data.sort(key=lambda t: t[0], reverse=reverse)
        for index, (val, k) in enumerate(data):
            tree.move(k, '', index)

        # Sortierstatus und Richtung merken
        if not hasattr(tree, '_sort_state'):
            tree._sort_state = {}
        tree._sort_state['col'] = col
        tree._sort_state['reverse'] = reverse

        # Alle Header zurücksetzen
        for c in tree['columns']:
            tree.heading(c, text=c, command=lambda c2=c, t=tree: self._treeview_sort_column(t, c2, False))

        # Sortierpfeil setzen
        arrow = ' ▲' if not reverse else ' ▼'
        tree.heading(col, text=col + arrow, command=lambda: self._treeview_sort_column(tree, col, not reverse))
    def __init__(self, root):
        self.root = root
        self.root.title('CSVLotte')
        # Fenstergröße initial, aber frei vergrößerbar
        self.root.geometry('900x500')
        self.root.resizable(True, True)
        self.file1_path = ''
        self.file2_path = ''
        self.df1 = None
        self.df2 = None
        # Fortschrittsbalken unter der Ergebnistabelle, volle Breite (immer sichtbar)
        self.progress = ttk.Progressbar(self.root, orient='horizontal', mode='determinate')
        self.progress.pack(side='bottom', fill='x', padx=10, pady=(0,10))
        # Fortschrittsbalken-Style für grün
        style = ttk.Style(self.root)
        style.theme_use('default')
        style.configure("green.Horizontal.TProgressbar", foreground='green', background='green')
        self.progress.configure(style="green.Horizontal.TProgressbar")
        # Fenster-Icon setzen (automatische Auswahl je nach Plattform)
        try:
            import os, sys
            base_dir = os.path.dirname(__file__)
            icon_img = None
            if sys.platform.startswith('win'):
                ico_path = os.path.join(base_dir, 'logo.ico')
                if os.path.exists(ico_path):
                    self.root.iconbitmap(ico_path)
                else:
                    png_path = os.path.join(base_dir, 'logo.png')
                    if os.path.exists(png_path):
                        icon_img = tk.PhotoImage(file=png_path)
                        self.root.iconphoto(True, icon_img)
            elif sys.platform == 'darwin':
                icns_path = os.path.join(base_dir, 'logo.icns')
                # .icns wird für App-Bundles genutzt, für Tkinter trotzdem PNG
                png_path = os.path.join(base_dir, 'logo.png')
                if os.path.exists(png_path):
                    icon_img = tk.PhotoImage(file=png_path)
                    self.root.iconphoto(True, icon_img)
            else:
                # Linux/sonstige: PNG
                png_path = os.path.join(base_dir, 'logo.png')
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
        tk.Button(file_row1, text='CSV 1 auswählen', command=self.load_file1).pack(side='left', padx=5, pady=5)
        self.file1_label = tk.Label(file_row1, text='Keine Datei gewählt')
        self.file1_label.pack(side='left', padx=5, pady=5)
        # Trennzeichen und Encoding für CSV1
        tk.Label(file_row1, text='Trennz.:').pack(side='left', padx=(10,0), pady=5)
        self.delim_var1 = tk.StringVar(value=';')
        self.delim_entry1 = tk.Entry(file_row1, textvariable=self.delim_var1, width=3)
        self.delim_entry1.pack(side='left', padx=2, pady=5)
        tk.Label(file_row1, text='Enc.').pack(side='left', padx=(5,0), pady=5)
        self.encoding_var1 = tk.StringVar(value='latin1')
        encodings = ['latin1', 'utf-8', 'cp1252', 'utf-16', 'iso-8859-1']
        self.encoding_combo1 = ttk.Combobox(file_row1, textvariable=self.encoding_var1, values=encodings, state='readonly', width=10)
        self.encoding_combo1.pack(side='left', padx=2, pady=5)
        self.delim_var1.trace_add('write', lambda *args: self.reload_file1() if self.file1_path else None)
        self.encoding_var1.trace_add('write', lambda *args: self.reload_file1() if self.file1_path else None)
        self.file1_reload_btn = tk.Button(file_row1, text='⟳', command=self.reload_file1, state='disabled', width=2)
        self.file1_reload_btn.pack(side='left', padx=(2,0), pady=5)
        self.file1_info_btn = tk.Button(file_row1, text='ℹ️', command=self.show_file1_info, state='disabled', width=2)
        self.file1_info_btn.pack(side='left', padx=2, pady=5)

        # WHERE-Filter für CSV 1
        filter_row1 = tk.Frame(self.control_frame)
        filter_row1.pack(anchor='w', fill='x', padx=5, pady=(0,2))
        tk.Label(filter_row1, text='Filter (WHERE SQL):').pack(side='left', padx=(0,2), pady=2)
        self.filter1_var = tk.StringVar()
        self.filter1_entry = tk.Entry(filter_row1, textvariable=self.filter1_var, width=50)
        self.filter1_entry.pack(side='left', padx=2, pady=2)
        self.filter1_btn = tk.Button(filter_row1, text='...', width=2, command=self.open_filter1_window)
        self.filter1_btn.pack(side='left', padx=(2,0), pady=2)

        # ...existing code...

        file_row2 = tk.Frame(self.control_frame)
        file_row2.pack(anchor='w', fill='x')
        tk.Button(file_row2, text='CSV 2 auswählen', command=self.load_file2).pack(side='left', padx=5, pady=5)
        self.file2_label = tk.Label(file_row2, text='Keine Datei gewählt')
        self.file2_label.pack(side='left', padx=5, pady=5)
        # Trennzeichen und Encoding für CSV2
        tk.Label(file_row2, text='Trennz.:').pack(side='left', padx=(10,0), pady=5)
        self.delim_var2 = tk.StringVar(value=';')
        self.delim_entry2 = tk.Entry(file_row2, textvariable=self.delim_var2, width=3)
        self.delim_entry2.pack(side='left', padx=2, pady=5)
        tk.Label(file_row2, text='Enc.').pack(side='left', padx=(5,0), pady=5)
        self.encoding_var2 = tk.StringVar(value='latin1')
        self.encoding_combo2 = ttk.Combobox(file_row2, textvariable=self.encoding_var2, values=encodings, state='readonly', width=10)
        self.encoding_combo2.pack(side='left', padx=2, pady=5)
        self.delim_var2.trace_add('write', lambda *args: self.reload_file2() if self.file2_path else None)
        self.encoding_var2.trace_add('write', lambda *args: self.reload_file2() if self.file2_path else None)
        self.file2_reload_btn = tk.Button(file_row2, text='⟳', command=self.reload_file2, state='disabled', width=2)
        self.file2_reload_btn.pack(side='left', padx=(2,0), pady=5)
        self.file2_info_btn = tk.Button(file_row2, text='ℹ️', command=self.show_file2_info, state='disabled', width=2)
        self.file2_info_btn.pack(side='left', padx=2, pady=5)

        # WHERE-Filter für CSV 2 (jetzt direkt unter Dateiauswahl)
        filter_row2 = tk.Frame(self.control_frame)
        filter_row2.pack(anchor='w', fill='x', padx=5, pady=(0,2))
        tk.Label(filter_row2, text='Filter (WHERE SQL):').pack(side='left', padx=(0,2), pady=2)
        self.filter2_var = tk.StringVar()
        self.filter2_entry = tk.Entry(filter_row2, textvariable=self.filter2_var, width=50)
        self.filter2_entry.pack(side='left', padx=2, pady=2)
        self.filter2_btn = tk.Button(filter_row2, text='...', width=2, command=self.open_filter2_window)
        self.filter2_btn.pack(side='left', padx=(2,0), pady=2)

        # Comparison column selectors: stacked vertically, left-aligned
        col_frame = tk.Frame(self.control_frame)
        col_frame.pack(anchor='w', fill='x')
        # Column 1
        row_col1 = tk.Frame(col_frame)
        row_col1.pack(anchor='w', fill='x')
        tk.Label(row_col1, text='Vergleichsspalte CSV 1:').pack(side='left', padx=5, pady=5)
        self.column_combo1 = ttk.Combobox(row_col1, state='readonly')
        self.column_combo1.pack(side='left', padx=5, pady=5)
        # Label und Textfeld für Slice-Eingabe rechts neben der Spaltenauswahl 1
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
        # Label und Textfeld für Slice-Eingabe rechts neben der Spaltenauswahl 2
        tk.Label(row_col2, text='Slice:').pack(side='left', padx=(10,2), pady=5)
        self.col2_text_var = tk.StringVar()
        self.col2_text_entry = tk.Entry(row_col2, textvariable=self.col2_text_var, width=7)
        self.col2_text_entry.pack(side='left', padx=2, pady=5)

        # Vergleichsbutton und Exportbutton
        row5 = tk.Frame(self.control_frame)
        row5.pack(anchor='w', fill='x')
        self.compare_btn = tk.Button(row5, text='Vergleichen', command=self.compare_csvs, state='disabled')
        self.compare_btn.pack(side='left', padx=5, pady=10)
        self.export_btn = tk.Button(row5, text='Exportiere Ergebnisse', command=self.export_results_button, state='disabled')
        self.export_btn.pack(side='left', padx=5, pady=10)

        # Ergebnisanzeige: Eine Tabelle über die gesamte Breite, mit Dropdown zur Auswahl
        # Ergebnisanzeige: Eine Tabelle über die gesamte Breite, mit Dropdown zur Auswahl
        # Das Ergebnis-Frame füllt das Fenster (außer oben die Steuerelemente und unten der Fortschrittsbalken)
        result_frame = tk.Frame(self.root)
        result_frame.pack(padx=10, pady=10, fill='both', expand=True)
        result_frame.rowconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)
        self.result_table_labels = ['Nur in CSV 1', 'Gemeinsam', 'Nur in CSV 2']
        self.notebook = ttk.Notebook(result_frame)
        self.notebook.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)
        self.result_table_frames = []
        self.result_tables = []
        self._result_dfs = [None, None, None]
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

    def open_filter1_window(self):
        self._open_filter_window(self.filter1_var, 'Filter für CSV 1')

    def open_filter2_window(self):
        self._open_filter_window(self.filter2_var, 'Filter für CSV 2')

    def _open_filter_window(self, var, title):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.grab_set()
        win.resizable(True, True)
        # Setze Fenstergröße auf 2/3 der Bildschirmgröße
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        width = int(screen_w * 2 / 3)
        height = int(screen_h * 2 / 3)
        # Fenster mittig auf dem Bildschirm öffnen
        x = (screen_w // 2) - (width // 2)
        y = (screen_h // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")

        # Tabelle oben (mit Scrollbars direkt am Widget)
        table_frame = tk.Frame(win)
        table_frame.pack(fill='both', expand=True, side='top', padx=10, pady=(10, 2))
        tree = ttk.Treeview(table_frame, show='headings')
        tree.grid(row=0, column=0, sticky='nsew')
        xscroll = ttk.Scrollbar(table_frame, orient='horizontal', command=tree.xview)
        xscroll.grid(row=1, column=0, sticky='ew')
        tree.configure(xscrollcommand=xscroll.set)
        yscroll = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        yscroll.grid(row=0, column=1, sticky='ns')
        tree.configure(yscrollcommand=yscroll.set)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # Hilfsfunktion für Sortierung
        def sort_column(col, reverse):
            data = [(tree.set(k, col), k) for k in tree.get_children('')]
            try:
                data.sort(key=lambda t: float(t[0].replace(',', '.')), reverse=reverse)
            except Exception:
                data.sort(key=lambda t: t[0], reverse=reverse)
            for index, (val, k) in enumerate(data):
                tree.move(k, '', index)
            # Sortierstatus und Richtung merken
            if not hasattr(tree, '_sort_state'):
                tree._sort_state = {}
            tree._sort_state['col'] = col
            tree._sort_state['reverse'] = reverse
            # Alle Header zurücksetzen
            for c in tree['columns']:
                tree.heading(c, text=c, command=lambda c2=c: sort_column(c2, False))
            # Sortierpfeil setzen
            arrow = ' ▲' if not reverse else ' ▼'
            tree.heading(col, text=col + arrow, command=lambda: sort_column(col, not reverse))

        # Filtereingabe und Buttons unten
        bottom_frame = tk.Frame(win)
        bottom_frame.pack(side='bottom', fill='x', padx=10, pady=10)
        tk.Label(bottom_frame, text='Filter:').pack(side='left', padx=(0, 5))
        text = tk.Text(bottom_frame, height=1)
        text.pack(side='left', padx=(0, 5), fill='x', expand=True)
        text.insert('1.0', var.get())

        # Buttons wieder anzeigen und korrekt platzieren
        btn_frame = tk.Frame(bottom_frame)
        btn_frame.pack(side='left', padx=5)
        def apply_and_update():
            var.set(text.get('1.0', 'end').strip())
            # Filter neu anwenden und Tabelle aktualisieren
            filter_str = text.get('1.0', 'end').strip()
            nonlocal df_filtered
            df_filtered = df
            for widget in tree.get_children():
                tree.delete(widget)
            if df is not None and filter_str:
                try:
                    from sqlfilter import sql_where_to_pandas
                    query_str = filter_str
                    if query_str.lower().startswith('where '):
                        query_str = query_str[6:]
                    query_str = sql_where_to_pandas(query_str)
                    mask = df.eval(query_str)
                    df_filtered = df[mask]
                except Exception as e:
                    err_lbl = tk.Label(win, text=f'Filterfehler: {e}', fg='red')
                    err_lbl.pack()
                    df_filtered = None
            if df_filtered is not None and not df_filtered.empty:
                cols = list(df_filtered.columns)
                tree['columns'] = cols
                for col in cols:
                    tree.heading(col, text=col, command=lambda c=col: sort_column(c, False))
                    tree.column(col, width=120, anchor='w', stretch=False)
                for _, row in df_filtered.iterrows():
                    values = tuple("" if pd.isna(row[col]) else row[col] for col in df_filtered.columns)
                    tree.insert('', 'end', values=values)
            else:
                tree['columns'] = []
            # Nach Filter-Übernahme Datei neu laden, damit der Vergleich den Filter berücksichtigt
            if '1' in title:
                self.reload_file1()
            else:
                self.reload_file2()
        def export_df():
            import os
            from tkinter import filedialog, messagebox
            df_export = df_filtered
            if df_export is None or df_export.empty:
                messagebox.showerror('Export', 'Keine Daten zum Exportieren.')
                return
            # Export-Dialogfenster öffnen
            export_win = tk.Toplevel(win)
            export_win.title('Exportieren')
            export_win.grab_set()
            export_win.resizable(False, False)
            # Speicherort (default: Verzeichnis der jeweiligen CSV-Datei)
            if '1' in title and self.file1_path:
                default_dir = os.path.dirname(self.file1_path)
                default_name = os.path.splitext(os.path.basename(self.file1_path))[0] + '_filtered.csv'
            elif '2' in title and self.file2_path:
                default_dir = os.path.dirname(self.file2_path)
                default_name = os.path.splitext(os.path.basename(self.file2_path))[0] + '_filtered.csv'
            else:
                default_dir = os.getcwd()
                default_name = 'filtered.csv'
            # Trennzeichen
            tk.Label(export_win, text='Trennzeichen:').grid(row=0, column=0, sticky='w', padx=10, pady=5)
            delim_var = tk.StringVar(value=';')
            delim_entry = tk.Entry(export_win, textvariable=delim_var, width=3)
            delim_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)
            # Encoding
            tk.Label(export_win, text='Encoding:').grid(row=0, column=2, sticky='w', padx=5, pady=5)
            encoding_var = tk.StringVar(value='latin1')
            encoding_combo = ttk.Combobox(export_win, textvariable=encoding_var, values=['latin1', 'utf-8', 'cp1252', 'utf-16', 'iso-8859-1'], state='readonly', width=10)
            encoding_combo.grid(row=0, column=3, sticky='w', padx=5, pady=5)
            # Speicherort
            tk.Label(export_win, text='Speicherort:').grid(row=1, column=0, sticky='w', padx=10, pady=5)
            path_var = tk.StringVar(value=default_dir)
            path_entry = tk.Entry(export_win, textvariable=path_var, width=40)
            path_entry.grid(row=1, column=1, columnspan=2, sticky='w', padx=5, pady=5)
            def choose_dir():
                d = filedialog.askdirectory(initialdir=default_dir)
                if d:
                    path_var.set(d)
            tk.Button(export_win, text='Ordner wählen...', command=choose_dir).grid(row=1, column=3, sticky='w', padx=5, pady=5)
            # Dateiname
            tk.Label(export_win, text='Dateiname:').grid(row=2, column=0, sticky='w', padx=10, pady=5)
            name_var = tk.StringVar(value=default_name)
            name_entry = tk.Entry(export_win, textvariable=name_var, width=30)
            name_entry.grid(row=2, column=1, columnspan=2, sticky='w', padx=5, pady=5)
            # Exportieren-Button
            def do_export():
                out_dir = path_var.get()
                out_name = name_var.get()
                if not out_name.lower().endswith('.csv'):
                    out_name += '.csv'
                out_path = os.path.join(out_dir, out_name)
                delim = delim_var.get() if delim_var.get() else ';'
                encoding = encoding_var.get() if encoding_var.get() else 'latin1'
                # Prüfen ob Datei existiert
                if os.path.exists(out_path):
                    overwrite = messagebox.askyesno('Datei existiert', f'Die Datei {out_path} existiert bereits. Überschreiben?')
                    if not overwrite:
                        return
                try:
                    df_export.to_csv(out_path, index=False, sep=delim, encoding=encoding)
                    messagebox.showinfo('Export', f'Datei erfolgreich exportiert nach:\n{out_path}')
                    export_win.destroy()
                except Exception as e:
                    messagebox.showerror('Export', f'Fehler beim Exportieren: {e}')
            tk.Button(export_win, text='Exportieren', command=do_export).grid(row=3, column=0, columnspan=4, pady=10)
            # Fenster mittig setzen
            export_win.update_idletasks()
            x = win.winfo_x() + (win.winfo_width() // 2) - (export_win.winfo_width() // 2)
            y = win.winfo_y() + (win.winfo_height() // 2) - (export_win.winfo_height() // 2)
            export_win.geometry(f'+{x}+{y}')
        tk.Button(btn_frame, text='Übernehmen', command=apply_and_update).pack(side='left', padx=5)
        tk.Button(btn_frame, text='Exportieren', command=export_df).pack(side='left', padx=5)

        # Bestimme, welche DataFrame angezeigt werden soll
        if '1' in title:
            df = self.df1
        else:
            df = self.df2
        # Filter anwenden, falls gesetzt
        filter_str = text.get('1.0', 'end').strip()
        df_filtered = df
        if df is not None and filter_str:
            try:
                from sqlfilter import sql_where_to_pandas
                query_str = filter_str
                if query_str.lower().startswith('where '):
                    query_str = query_str[6:]
                query_str = sql_where_to_pandas(query_str)
                mask = df.eval(query_str)
                df_filtered = df[mask]
            except Exception as e:
                # Fehleranzeige im Fenster
                err_lbl = tk.Label(win, text=f'Filterfehler: {e}', fg='red')
                err_lbl.pack()
                df_filtered = None
        # Tabelle befüllen
        if df_filtered is not None and not df_filtered.empty:
            cols = list(df_filtered.columns)
            tree['columns'] = cols
            for col in cols:
                tree.heading(col, text=col, command=lambda c=col: sort_column(c, False))
                tree.column(col, width=120, anchor='w', stretch=False)
            for _, row in df_filtered.iterrows():
                values = tuple("" if pd.isna(row[col]) else row[col] for col in df_filtered.columns)
                tree.insert('', 'end', values=values)
        else:
            tree['columns'] = []

        # Fenster mittig setzen
        win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (win.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (win.winfo_height() // 2)
        win.geometry(f'+{x}+{y}')

    def update_tab_labels(self):
        # Setze die Tab-Texte dynamisch nach Dateinamen
        file1 = self.file1_path.split('/')[-1] if self.file1_path else 'CSV 1'
        file2 = self.file2_path.split('/')[-1] if self.file2_path else 'CSV 2'
        labels = [f'Nur in {file1}', 'Gemeinsam', f'Nur in {file2}']
        for i, label in enumerate(labels):
            self.notebook.tab(i, text=label)

        self.column_combo1.bind('<<ComboboxSelected>>', self.sync_column_selection)

        # Fortschrittsbalken wird jetzt immer im Konstruktor erzeugt

    def load_file1(self):
        path = filedialog.askopenfilename(filetypes=[('CSV files', '*.csv')])
        if path:
            self.file1_path = path
            self.file1_label.config(text=path)
            self.file1_info_btn.config(state='normal')
            self.file1_reload_btn.config(state='normal')
            delim = self.delim_var1.get() if self.delim_var1.get() else ';'
            encoding = self.encoding_var1.get() if self.encoding_var1.get() else 'latin1'
            try:
                df = pd.read_csv(path, delimiter=delim, encoding=encoding, engine='python')
            except Exception as e:
                if encoding != 'utf-8':
                    try:
                        df = pd.read_csv(path, delimiter=delim, encoding='utf-8', engine='python')
                        messagebox.showinfo('Hinweis', 'Datei wurde mit utf-8 statt latin1 geladen.')
                    except Exception as e2:
                        messagebox.showerror('Fehler', f'CSV konnte nicht geladen werden: {e2}')
                        df = None
                else:
                    messagebox.showerror('Fehler', f'CSV konnte nicht geladen werden: {e}')
                    df = None
            # Filter anwenden, falls gesetzt
            if df is not None:
                from sqlfilter import sql_where_to_pandas
                filter_str = self.filter1_var.get().strip()
                if filter_str:
                    try:
                        query_str = filter_str
                        if query_str.lower().startswith('where '):
                            query_str = query_str[6:]
                        query_str = sql_where_to_pandas(query_str)
                        mask = df.eval(query_str)
                        df = df[mask]
                    except Exception as e:
                        messagebox.showerror('Fehler', f'Filter konnte nicht angewendet werden:\n{e}')
                self.df1 = df
            else:
                self.df1 = None
            self.update_columns()
            self.enable_compare_btn()
            self.update_tab_labels()

    def load_file2(self):
        path = filedialog.askopenfilename(filetypes=[('CSV files', '*.csv')])
        if path:
            self.file2_path = path
            self.file2_label.config(text=path)
            self.file2_info_btn.config(state='normal')
            self.file2_reload_btn.config(state='normal')
            delim = self.delim_var2.get() if self.delim_var2.get() else ';'
            encoding = self.encoding_var2.get() if self.encoding_var2.get() else 'latin1'
            try:
                df = pd.read_csv(path, delimiter=delim, encoding=encoding, engine='python')
            except Exception as e:
                if encoding != 'utf-8':
                    try:
                        df = pd.read_csv(path, delimiter=delim, encoding='utf-8', engine='python')
                        messagebox.showinfo('Hinweis', 'Datei wurde mit utf-8 statt latin1 geladen.')
                    except Exception as e2:
                        messagebox.showerror('Fehler', f'CSV konnte nicht geladen werden: {e2}')
                        df = None
                else:
                    messagebox.showerror('Fehler', f'CSV konnte nicht geladen werden: {e}')
                    df = None
            # Filter anwenden, falls gesetzt
            if df is not None:
                from sqlfilter import sql_where_to_pandas
                filter_str = self.filter2_var.get().strip()
                if filter_str:
                    try:
                        query_str = filter_str
                        if query_str.lower().startswith('where '):
                            query_str = query_str[6:]
                        query_str = sql_where_to_pandas(query_str)
                        mask = df.eval(query_str)
                        df = df[mask]
                    except Exception as e:
                        messagebox.showerror('Fehler', f'Filter konnte nicht angewendet werden:\n{e}')
                self.df2 = df
            else:
                self.df2 = None
            self.update_columns()
            self.enable_compare_btn()
            self.update_tab_labels()

    def reload_file1(self):
        if self.file1_path:
            delim = self.delim_var1.get() if self.delim_var1.get() else ';'
            encoding = self.encoding_var1.get() if self.encoding_var1.get() else 'latin1'
            try:
                df = pd.read_csv(self.file1_path, delimiter=delim, encoding=encoding, engine='python')
            except Exception as e:
                if encoding != 'utf-8':
                    try:
                        df = pd.read_csv(self.file1_path, delimiter=delim, encoding='utf-8', engine='python')
                        messagebox.showinfo('Hinweis', 'Datei wurde mit utf-8 statt latin1 geladen.')
                    except Exception as e2:
                        messagebox.showerror('Fehler', f'CSV konnte nicht geladen werden: {e2}')
                        df = None
                else:
                    messagebox.showerror('Fehler', f'CSV konnte nicht geladen werden: {e}')
                    df = None
            # Filter anwenden, falls gesetzt
            if df is not None:
                from sqlfilter import sql_where_to_pandas
                filter_str = self.filter1_var.get().strip()
                if filter_str:
                    try:
                        query_str = filter_str
                        if query_str.lower().startswith('where '):
                            query_str = query_str[6:]
                        query_str = sql_where_to_pandas(query_str)
                        mask = df.eval(query_str)
                        df = df[mask]
                    except Exception as e:
                        messagebox.showerror('Fehler', f'Filter konnte nicht angewendet werden:\n{e}')
                self.df1 = df
            else:
                self.df1 = None
            self.update_columns()
            self.enable_compare_btn()
            if self.df2 is not None:
                self.compare_csvs()

    def reload_file2(self):
        if self.file2_path:
            delim = self.delim_var2.get() if self.delim_var2.get() else ';'
            encoding = self.encoding_var2.get() if self.encoding_var2.get() else 'latin1'
            try:
                df = pd.read_csv(self.file2_path, delimiter=delim, encoding=encoding, engine='python')
            except Exception as e:
                if encoding != 'utf-8':
                    try:
                        df = pd.read_csv(self.file2_path, delimiter=delim, encoding='utf-8', engine='python')
                        messagebox.showinfo('Hinweis', 'Datei wurde mit utf-8 statt latin1 geladen.')
                    except Exception as e2:
                        messagebox.showerror('Fehler', f'CSV konnte nicht geladen werden: {e2}')
                        df = None
                else:
                    messagebox.showerror('Fehler', f'CSV konnte nicht geladen werden: {e}')
                    df = None
            # Filter anwenden, falls gesetzt
            if df is not None:
                from sqlfilter import sql_where_to_pandas
                filter_str = self.filter2_var.get().strip()
                if filter_str:
                    try:
                        query_str = filter_str
                        if query_str.lower().startswith('where '):
                            query_str = query_str[6:]
                        query_str = sql_where_to_pandas(query_str)
                        mask = df.eval(query_str)
                        df = df[mask]
                    except Exception as e:
                        messagebox.showerror('Fehler', f'Filter konnte nicht angewendet werden:\n{e}')
                self.df2 = df
            else:
                self.df2 = None
            self.update_columns()
            self.enable_compare_btn()
            if self.df1 is not None:
                self.compare_csvs()

    def enable_compare_btn(self):
        if self.df1 is not None and self.df2 is not None:
            self.compare_btn.config(state='normal')
        else:
            self.compare_btn.config(state='disabled')

    def update_columns(self):
        if self.df1 is not None:
            self.column_combo1['values'] = list(self.df1.columns)
            if len(self.df1.columns) > 0:
                self.column_combo1.current(0)
        if self.df2 is not None:
            self.column_combo2['values'] = list(self.df2.columns)
            if len(self.df2.columns) > 0:
                self.column_combo2.current(0)
        # Export-Button deaktivieren, wenn neue Datei geladen wird
        if hasattr(self, 'export_btn'):
            self.export_btn.config(state='disabled')

    def sync_column_selection(self, event=None):
        selected_col1 = self.column_combo1.get()
        if self.df2 is not None and selected_col1:
            cols2 = list(self.df2.columns)
            if selected_col1 in cols2:
                self.column_combo2.set(selected_col1)

    def compare_csvs(self):
        import time
        col1 = self.column_combo1.get()
        col2 = self.column_combo2.get()
        if not col1 or not col2:
            messagebox.showerror('Fehler', 'Bitte Vergleichsspalten für beide Dateien wählen!')
            return
        if self.df1 is None or self.df2 is None:
            messagebox.showerror('Fehler', 'Bitte beide CSV-Dateien laden!')
            return

        # Slice-Strings aus den Textfeldern holen
        slice1_str = self.col1_text_var.get().strip()
        slice2_str = self.col2_text_var.get().strip()

        def apply_slice(series, slice_str):
            if not slice_str:
                return series
            try:
                # Akzeptiere alle Python-Slice-Varianten wie -2:, :5, ::-1 usw.
                parts = slice_str.split(':')
                # Fülle fehlende Teile mit None auf
                while len(parts) < 3:
                    parts.append('')
                start = parts[0].strip() or None
                stop = parts[1].strip() or None
                step = parts[2].strip() or None
                # Konvertiere zu int oder None
                def to_int_or_none(val):
                    if val is None:
                        return None
                    try:
                        return int(val)
                    except Exception:
                        return None
                s = slice(to_int_or_none(start), to_int_or_none(stop), to_int_or_none(step))
                return series.apply(lambda x: x[s] if isinstance(x, str) else x)
            except Exception as e:
                messagebox.showerror('Fehler', f'Slice-Syntax ungültig: "{slice_str}"\n{e}')
                return series

        # Fortschrittsbalken initialisieren
        self.progress.configure(style="Horizontal.TProgressbar")
        self.progress['value'] = 0
        self.progress.update_idletasks()

        # Schritt 1: Sets bilden (ggf. mit Slice)
        series1 = self.df1[col1]
        series2 = self.df2[col2]
        if slice1_str:
            series1 = apply_slice(series1, slice1_str)
        if slice2_str:
            series2 = apply_slice(series2, slice2_str)
        set1 = set(series1)
        self.progress['value'] = 20
        self.progress.update_idletasks()
        set2 = set(series2)
        self.progress['value'] = 40
        self.progress.update_idletasks()
        common = set1 & set2
        self.progress['value'] = 60
        self.progress.update_idletasks()
        only1 = set1 - set2
        only2 = set2 - set1
        self.progress['value'] = 70
        self.progress.update_idletasks()

        # Schritt 2: DataFrames für die Ergebnisse (mit Slices)
        mask1 = series1.isin(only1)
        mask_common = series1.isin(common)
        mask2 = series2.isin(only2)
        df_only1 = self.df1[mask1]
        self.progress['value'] = 80
        self.progress.update_idletasks()
        df_common1 = self.df1[mask_common]
        self.progress['value'] = 90
        self.progress.update_idletasks()
        df_only2 = self.df2[mask2]
        self.progress['value'] = 95
        self.progress.update_idletasks()

        # Ergebnis-DataFrames speichern
        dfs = [df_only1, df_common1, df_only2]
        self._result_dfs = dfs
        # Tabs aktivieren
        for i in range(len(self.result_table_labels)):
            self.notebook.tab(i, state='normal')
        # Export-Button aktivieren
        self.export_btn.config(state='normal')
        # Tab-Auswahl steuern: beim ersten Vergleich auf "Gemeinsam", sonst aktuelle Auswahl beibehalten
        current_tab = self.notebook.index(self.notebook.select()) if self.notebook.select() else None
        if not hasattr(self, '_has_compared') or not self._has_compared:
            self.notebook.select(1)  # "Gemeinsam"-Tab
            self._has_compared = True
        elif current_tab is not None:
            self.notebook.select(current_tab)
        self.update_result_table_view()

        # Fortschrittsbalken grün und voll
        style = ttk.Style(self.root)
        style.configure("green.Horizontal.TProgressbar", foreground='green', background='green')
        self.progress.configure(style="green.Horizontal.TProgressbar")
        self.progress['value'] = 100
        self.progress.update_idletasks()

    def update_result_table_view(self, event=None):
        # Aktualisiere alle Tabs/Trees entsprechend der gespeicherten DataFrames
        for idx, tree in enumerate(self.result_tables):
            df = self._result_dfs[idx] if self._result_dfs and self._result_dfs[idx] is not None else None
            # Tabelle leeren
            for item in tree.get_children():
                tree.delete(item)
            if df is not None and not df.empty:
                cols = list(df.columns)
                tree['columns'] = cols
                # Prüfe, ob vorher sortiert wurde
                sort_col = None
                sort_reverse = False
                if hasattr(tree, '_sort_state'):
                    sort_col = tree._sort_state.get('col')
                    sort_reverse = tree._sort_state.get('reverse', False)
                for col in cols:
                    # Spaltenüberschrift mit Sortierfunktion
                    tree.heading(col, text=col, command=lambda c=col, t=tree: self._treeview_sort_column(t, c, False))
                    tree.column(col, width=120, anchor='w', stretch=False)
                # Sortierpfeil ggf. wiederherstellen
                if sort_col in cols:
                    arrow = ' ▲' if not sort_reverse else ' ▼'
                    tree.heading(sort_col, text=sort_col + arrow, command=lambda: self._treeview_sort_column(tree, sort_col, not sort_reverse))
                # NaN-Werte als leere Strings anzeigen
                for _, row in df.iterrows():
                    values = tuple("" if pd.isna(row[col]) else row[col] for col in df.columns)
                    tree.insert('', 'end', values=values)
            else:
                tree['columns'] = []
                # Keine Daten

    def export_results(self, col1, col2):
        if self.df1 is None or self.df2 is None or not col1 or not col2:
            messagebox.showerror('Fehler', 'Bitte beide CSV-Dateien laden und Vergleichsspalten wählen!')
            return
        set1 = set(self.df1[col1])
        set2 = set(self.df2[col2])
        common = set1 & set2
        only1 = set1 - set2
        only2 = set2 - set1
        # Export common
        df_common = self.df1[self.df1[col1].isin(common)]
        df_common.to_csv('gemeinsame_werte.csv', index=False)
        # Export only in CSV 1
        df_only1 = self.df1[self.df1[col1].isin(only1)]
        df_only1.to_csv('nur_in_csv1.csv', index=False)
        # Export only in CSV 2
        df_only2 = self.df2[self.df2[col2].isin(only2)]
        df_only2.to_csv('nur_in_csv2.csv', index=False)
        messagebox.showinfo('Export', 'Ergebnisse wurden als gemeinsame_werte.csv, nur_in_csv1.csv und nur_in_csv2.csv gespeichert.')

    def export_results_button(self):
        import os
        from tkinter import simpledialog
        # Aktuellen Tab und zugehörigen DataFrame bestimmen
        current_tab = self.notebook.index(self.notebook.select())
        df = self._result_dfs[current_tab] if self._result_dfs and self._result_dfs[current_tab] is not None else None
        if df is None or df.empty:
            messagebox.showerror('Export', 'Keine Daten zum Exportieren im ausgewählten Tab.')
            return
        # Dialogfenster für Exportoptionen
        export_win = tk.Toplevel(self.root)
        export_win.title('Exportieren')
        export_win.grab_set()
        export_win.resizable(False, False)
        # Ergebnis-Auswahl
        tk.Label(export_win, text='Welches Ergebnis exportieren?').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        result_var = tk.StringVar(value=str(current_tab))
        for i, label in enumerate(self.result_table_labels):
            tk.Radiobutton(export_win, text=label, variable=result_var, value=str(i)).grid(row=0, column=i+1, sticky='w', padx=5, pady=5)
        # Spalten-Auswahl (jetzt: auszuschließende Spalten per Listbox)
        tk.Label(export_win, text='Spalten NICHT exportieren:').grid(row=1, column=0, sticky='nw', padx=10, pady=5)
        listbox = tk.Listbox(export_win, selectmode='multiple', height=8, exportselection=0)
        for col in df.columns:
            listbox.insert('end', col)
        listbox.grid(row=1, column=1, columnspan=3, sticky='w', padx=5, pady=5)
        listbox.config(width=40)
        # Zielpfad
        tk.Label(export_win, text='Zielordner:').grid(row=2, column=0, sticky='w', padx=10, pady=5)
        default_dir = os.path.dirname(self.file1_path) if self.file1_path else os.getcwd()
        path_var = tk.StringVar(value=default_dir)
        path_entry = tk.Entry(export_win, textvariable=path_var, width=40)
        path_entry.grid(row=2, column=1, columnspan=2, sticky='w', padx=5, pady=5)
        def choose_dir():
            d = filedialog.askdirectory(initialdir=default_dir)
            if d:
                path_var.set(d)
        tk.Button(export_win, text='Ordner wählen...', command=choose_dir).grid(row=2, column=3, sticky='w', padx=5, pady=5)
        # Dateiname
        tk.Label(export_win, text='Dateiname:').grid(row=3, column=0, sticky='w', padx=10, pady=5)
        default_name = self.result_table_labels[current_tab].replace(' ', '_').replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss') + '.csv'
        name_var = tk.StringVar(value=default_name)
        name_entry = tk.Entry(export_win, textvariable=name_var, width=30)
        name_entry.grid(row=3, column=1, columnspan=2, sticky='w', padx=5, pady=5)
        # Encoding und Trennzeichen für Export
        tk.Label(export_win, text='Trennzeichen:').grid(row=4, column=0, sticky='w', padx=10, pady=5)
        export_delim_var = tk.StringVar(value=';')
        export_delim_entry = tk.Entry(export_win, textvariable=export_delim_var, width=3)
        export_delim_entry.grid(row=4, column=1, sticky='w', padx=5, pady=5)
        tk.Label(export_win, text='Encoding:').grid(row=4, column=2, sticky='w', padx=5, pady=5)
        export_encoding_var = tk.StringVar(value='latin1')
        export_encoding_combo = ttk.Combobox(export_win, textvariable=export_encoding_var, values=['latin1', 'utf-8', 'cp1252', 'utf-16', 'iso-8859-1'], state='readonly', width=10)
        export_encoding_combo.grid(row=4, column=3, sticky='w', padx=5, pady=5)
        # Exportieren-Button
        def do_export():
            idx = int(result_var.get())
            export_df = self._result_dfs[idx]
            # Spalten, die nicht exportiert werden sollen
            exclude_indices = listbox.curselection()
            exclude_cols = [df.columns[i] for i in exclude_indices]
            selected_cols = [col for col in export_df.columns if col not in exclude_cols]
            if not selected_cols:
                messagebox.showerror('Export', 'Bitte mindestens eine Spalte exportieren!')
                return
            out_dir = path_var.get()
            out_name = name_var.get()
            if not out_name.lower().endswith('.csv'):
                out_name += '.csv'
            out_path = os.path.join(out_dir, out_name)
            delim = export_delim_var.get() if export_delim_var.get() else ';'
            encoding = export_encoding_var.get() if export_encoding_var.get() else 'latin1'
            # Prüfen ob Datei existiert
            if os.path.exists(out_path):
                overwrite = messagebox.askyesno('Datei existiert', f'Die Datei {out_path} existiert bereits. Überschreiben?')
                if not overwrite:
                    return
            try:
                export_df[selected_cols].to_csv(out_path, index=False, sep=delim, encoding=encoding)
                messagebox.showinfo('Export', f'Datei erfolgreich exportiert nach:\n{out_path}')
                export_win.destroy()
            except Exception as e:
                messagebox.showerror('Export', f'Fehler beim Exportieren: {e}')
        tk.Button(export_win, text='Exportieren', command=do_export).grid(row=5, column=0, columnspan=4, pady=10)
        # Fenster mittig setzen
        export_win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (export_win.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (export_win.winfo_height() // 2)
        export_win.geometry(f'+{x}+{y}')

    def show_file1_info(self):
        if self.file1_path and self.df1 is not None:
            import os
            size_mb = os.path.getsize(self.file1_path) / (1024*1024)
            n_cols = len(self.df1.columns)
            n_rows = len(self.df1)  # ohne Titelzeile
            msg = f"Datei: {self.file1_path}\nSpalten: {n_cols}\nZeilen: {n_rows}\nDateigröße: {size_mb:.2f} MB"
            messagebox.showinfo('CSV 1 Info', msg)

    def show_file2_info(self):
        if self.file2_path and self.df2 is not None:
            import os
            size_mb = os.path.getsize(self.file2_path) / (1024*1024)
            n_cols = len(self.df2.columns)
            n_rows = len(self.df2)  # ohne Titelzeile
            msg = f"Datei: {self.file2_path}\nSpalten: {n_cols}\nZeilen: {n_rows}\nDateigröße: {size_mb:.2f} MB"
            messagebox.showinfo('CSV 2 Info', msg)

if __name__ == '__main__':
    root = tk.Tk()
    app = CSVLotteApp(root)
    root.mainloop()
