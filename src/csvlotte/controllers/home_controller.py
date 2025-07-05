from csvlotte.views.home_view import HomeView
import pandas as pd
from tkinter import filedialog, messagebox, ttk
from tkinter import ttk

class HomeController:
    def __init__(self, root):
        self.view = HomeView(root, self)

    # Datei 1 laden
    def load_file1(self):
        path = filedialog.askopenfilename(filetypes=[('CSV files', '*.csv')])
        if path:
            self.view.file1_path = path
            self.view.file1_label.config(text=path)
            self.view.file1_info_btn.config(state='normal')
            self.view.file1_reload_btn.config(state='normal')
            delim = self.view.delim_var1.get() if self.view.delim_var1.get() else ';'
            encoding = self.view.encoding_var1.get() if self.view.encoding_var1.get() else 'latin1'
            try:
                df = pd.read_csv(path, sep=delim, encoding=encoding)
                self.view.df1 = df
            except Exception as e:
                messagebox.showerror('Fehler', f'Datei 1 konnte nicht geladen werden:\n{e}')
                self.view.df1 = None
            # Filter anwenden, falls gesetzt
            if self.view.df1 is not None:
                filter_str = self.view.filter1_var.get().strip()
                if filter_str:
                    try:
                        self.view.df1 = self.view.df1.query(filter_str)
                    except Exception as e:
                        messagebox.showerror('Fehler', f'Filter für Datei 1 ungültig:\n{e}')
            self.update_columns()
            self.enable_compare_btn()
            self.update_tab_labels()
            self.view.update_filter_buttons()

    # Datei 2 laden
    def load_file2(self):
        path = filedialog.askopenfilename(filetypes=[('CSV files', '*.csv')])
        if path:
            self.view.file2_path = path
            self.view.file2_label.config(text=path)
            self.view.file2_info_btn.config(state='normal')
            self.view.file2_reload_btn.config(state='normal')
            delim = self.view.delim_var2.get() if self.view.delim_var2.get() else ';'
            encoding = self.view.encoding_var2.get() if self.view.encoding_var2.get() else 'latin1'
            try:
                df = pd.read_csv(path, sep=delim, encoding=encoding)
                self.view.df2 = df
            except Exception as e:
                messagebox.showerror('Fehler', f'Datei 2 konnte nicht geladen werden:\n{e}')
                self.view.df2 = None
            # Filter anwenden, falls gesetzt
            if self.view.df2 is not None:
                filter_str = self.view.filter2_var.get().strip()
                if filter_str:
                    try:
                        self.view.df2 = self.view.df2.query(filter_str)
                    except Exception as e:
                        messagebox.showerror('Fehler', f'Filter für Datei 2 ungültig:\n{e}')
            self.update_columns()
            self.enable_compare_btn()
            self.update_tab_labels()
            self.view.update_filter_buttons()

    # Datei 1 neu laden (z.B. nach Änderung von Encoding/Trennzeichen)
    def reload_file1(self):
        """
        Lädt die bereits gewählte Datei 1 erneut (z.B. nach Änderung von Encoding/Trennzeichen) und wendet ggf. den Filter an.
        """
        if self.view.file1_path:
            path = self.view.file1_path
            delim = self.view.delim_var1.get() if self.view.delim_var1.get() else ';'
            encoding = self.view.encoding_var1.get() if self.view.encoding_var1.get() else 'latin1'
            try:
                df = pd.read_csv(path, sep=delim, encoding=encoding)
                self.view.df1 = df
            except Exception as e:
                messagebox.showerror('Fehler', f'Datei 1 konnte nicht geladen werden:\n{e}')
                self.view.df1 = None
            # Filter anwenden, falls gesetzt
            if self.view.df1 is not None:
                filter_str = self.view.filter1_var.get().strip()
                if filter_str:
                    try:
                        from csvlotte.utils.helpers import sql_where_to_pandas
                        pandas_expr = sql_where_to_pandas(filter_str)
                        try:
                            self.view.df1 = self.view.df1.query(pandas_expr, engine="python")
                        except Exception:
                            self.view.df1 = self.view.df1.eval(pandas_expr)
                    except Exception as e:
                        messagebox.showerror('Fehler', f'Filter für Datei 1 ungültig:\n{e}')
            self.update_columns()
            self.enable_compare_btn()
            self.update_tab_labels()
            self.view.update_filter_buttons()

    # Datei 2 neu laden
    def reload_file2(self):
        """
        Lädt die bereits gewählte Datei 2 erneut (z.B. nach Änderung von Encoding/Trennzeichen) und wendet ggf. den Filter an.
        """
        if self.view.file2_path:
            path = self.view.file2_path
            delim = self.view.delim_var2.get() if self.view.delim_var2.get() else ';'
            encoding = self.view.encoding_var2.get() if self.view.encoding_var2.get() else 'latin1'
            try:
                df = pd.read_csv(path, sep=delim, encoding=encoding)
                self.view.df2 = df
            except Exception as e:
                messagebox.showerror('Fehler', f'Datei 2 konnte nicht geladen werden:\n{e}')
                self.view.df2 = None
            # Filter anwenden, falls gesetzt
            if self.view.df2 is not None:
                filter_str = self.view.filter2_var.get().strip()
                if filter_str:
                    try:
                        from csvlotte.utils.helpers import sql_where_to_pandas
                        pandas_expr = sql_where_to_pandas(filter_str)
                        try:
                            self.view.df2 = self.view.df2.query(pandas_expr, engine="python")
                        except Exception:
                            self.view.df2 = self.view.df2.eval(pandas_expr)
                    except Exception as e:
                        messagebox.showerror('Fehler', f'Filter für Datei 2 ungültig:\n{e}')
            self.update_columns()
            self.enable_compare_btn()
            self.update_tab_labels()
            self.view.update_filter_buttons()

    # Infofenster für Datei 1
    def show_file1_info(self):
        if self.view.file1_path and self.view.df1 is not None:
            import os
            try:
                size_kb = os.path.getsize(self.view.file1_path) / 1024
            except Exception:
                size_kb = 0
            info = f"Datei: {self.view.file1_path}\nGröße: {size_kb:.1f} kB\nZeilen: {len(self.view.df1)}\nSpalten: {len(self.view.df1.columns)}"
            messagebox.showinfo('Info Datei 1', info)

    # Infofenster für Datei 2
    def show_file2_info(self):
        if self.view.file2_path and self.view.df2 is not None:
            import os
            try:
                size_kb = os.path.getsize(self.view.file2_path) / 1024
            except Exception:
                size_kb = 0
            info = f"Datei: {self.view.file2_path}\nGröße: {size_kb:.1f} kB\nZeilen: {len(self.view.df2)}\nSpalten: {len(self.view.df2.columns)}"
            messagebox.showinfo('Info Datei 2', info)

    # Filterdialog für Datei 1
    def open_filter1_window(self):
        self.view.open_filter1_window()

    # Filterdialog für Datei 2
    def open_filter2_window(self):
        self.view.open_filter2_window()

    # Vergleichslogik
    def compare_csvs(self):
        col1 = self.view.column_combo1.get()
        col2 = self.view.column_combo2.get()
        if not col1 or not col2:
            messagebox.showerror('Fehler', 'Bitte Vergleichsspalten auswählen!')
            return
        if self.view.df1 is None or self.view.df2 is None:
            messagebox.showerror('Fehler', 'Bitte beide CSV-Dateien laden!')
            return
        slice1_str = self.view.col1_text_var.get().strip()
        slice2_str = self.view.col2_text_var.get().strip()
        def apply_slice(series, slice_str):
            if not slice_str:
                return series
            try:
                return series.str.slice(*[int(x) if x else None for x in (slice_str+':').split(':')[:2]])
            except Exception:
                return series
        self.view.progress.configure(style="Horizontal.TProgressbar")
        self.view.progress['value'] = 0
        self.view.progress.update_idletasks()
        series1 = self.view.df1[col1]
        series2 = self.view.df2[col2]
        if slice1_str:
            series1 = apply_slice(series1, slice1_str)
        if slice2_str:
            series2 = apply_slice(series2, slice2_str)
        set1 = set(series1)
        self.view.progress['value'] = 20
        self.view.progress.update_idletasks()
        set2 = set(series2)
        self.view.progress['value'] = 40
        self.view.progress.update_idletasks()
        common = set1 & set2
        self.view.progress['value'] = 60
        self.view.progress.update_idletasks()
        only1 = set1 - set2
        only2 = set2 - set1
        self.view.progress['value'] = 70
        self.view.progress.update_idletasks()
        mask1 = series1.isin(only1)
        mask_common1 = series1.isin(common)
        mask_common2 = series2.isin(common)
        mask2 = series2.isin(only2)
        df_only1 = self.view.df1[mask1]
        self.view.progress['value'] = 80
        self.view.progress.update_idletasks()
        df_common1 = self.view.df1[mask_common1]
        df_common2 = self.view.df2[mask_common2]
        self.view.progress['value'] = 90
        self.view.progress.update_idletasks()
        df_only2 = self.view.df2[mask2]
        self.view.progress['value'] = 95
        self.view.progress.update_idletasks()
        dfs = [df_only1, df_common1, df_common2, df_only2]
        self.view._result_dfs = dfs
        for i in range(len(self.view.result_table_labels)):
            self.view.notebook.tab(i, state='normal')
        self.view.export_btn.config(state='normal')
        current_tab = self.view.notebook.index(self.view.notebook.select()) if self.view.notebook.select() else None
        if not hasattr(self.view, '_has_compared') or not self.view._has_compared:
            self.view.notebook.select(1)
            self.view._has_compared = True
        elif current_tab is not None:
            self.view.notebook.select(current_tab)
        self.view.update_result_table_view()
        style = ttk.Style(self.view.root)
        style.configure("green.Horizontal.TProgressbar", foreground='green', background='green')
        self.view.progress.configure(style="green.Horizontal.TProgressbar")
        self.view.progress['value'] = 100
        self.view.progress.update_idletasks()

    # Export-Button
    def export_results_button(self):
        from csvlotte.controllers.compare_export_controller import CompareExportController
        current_tab = self.view.notebook.index(self.view.notebook.select())
        dfs = self.view._result_dfs
        result_table_labels = self.view.result_table_labels
        default_dir = None
        if hasattr(self.view, 'file1_path') and self.view.file1_path:
            import os
            default_dir = os.path.dirname(self.view.file1_path)
        controller = CompareExportController(self.view.root, dfs, result_table_labels, current_tab, default_dir)
        controller.open_export_dialog()

    # Hilfsmethoden
    def update_columns(self):
        if self.view.df1 is not None:
            self.view.column_combo1['values'] = list(self.view.df1.columns)
        if self.view.df2 is not None:
            self.view.column_combo2['values'] = list(self.view.df2.columns)
        if hasattr(self.view, 'export_btn'):
            self.view.export_btn.config(state='disabled')

    def enable_compare_btn(self):
        if self.view.df1 is not None and self.view.df2 is not None:
            self.view.compare_btn.config(state='normal')
        else:
            self.view.compare_btn.config(state='disabled')

    def update_tab_labels(self):
        file1 = self.view.file1_path.split('/')[-1] if self.view.file1_path else 'CSV 1'
        file2 = self.view.file2_path.split('/')[-1] if self.view.file2_path else 'CSV 2'
        labels = [
            f'Nur in {file1}',
            f'Gemeinsame {file1}',
            f'Gemeinsame in {file2}',
            f'Nur in {file2}'
        ]
        for i, label in enumerate(labels):
            self.view.notebook.tab(i, text=label)
        self.view.column_combo1.bind('<<ComboboxSelected>>', self.view.sync_column_selection)