"""
Module for HomeController: handles loading CSV files, applying filters, comparing data, and exporting results.
"""

from csvlotte.views.home_view import HomeView
import pandas as pd
from tkinter import filedialog, messagebox, ttk
from tkinter import ttk
from typing import Any

class HomeController:
    """
    Controller to manage user interactions: load CSVs, apply filters, compare data, and export results.
    """
    def __init__(self, root: Any) -> None:
        """
        Initialize the controller with the main application window.

        Args:
            root (Any): The root Tkinter window or parent widget.
        """
        self.view = HomeView(root, self)

    def load_file(self, file_num: int) -> None:
        """
        Open file dialog and load the specified CSV file into the view, applying optional filters.
        :param file_num: 1 for file1, 2 for file2
        """
        path = filedialog.askopenfilename(filetypes=[('CSV files', '*.csv')])
        if not path:
            return
        if file_num == 1:
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
            if self.view.df1 is not None:
                filter_str = self.view.filter1_var.get().strip()
                if filter_str:
                    try:
                        self.view.df1 = self.view.df1.query(filter_str)
                    except Exception as e:
                        messagebox.showerror('Fehler', f'Filter für Datei 1 ungültig:\n{e}')
        else:
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

    def reload_file1(self) -> None:
        """
        Reload the first CSV file (e.g., after changing delimiter or encoding) and reapply filters.
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
            if self.view.df1 is not None:
                filter_str = self.view.filter1_var.get().strip()
                if filter_str:
                    try:
                        from csvlotte.utils.helpers import sql_where_to_pandas
                        pandas_expr = sql_where_to_pandas(filter_str)
                        try:
                            df = self.view.df1
                            self.view.df1 = self.view.df1.query(pandas_expr, engine="python", local_dict={'df': df})
                        except Exception:
                            df = self.view.df1
                            self.view.df1 = self.view.df1.eval(pandas_expr)
                    except Exception as e:
                        messagebox.showerror('Fehler', f'Filter für Datei 1 ungültig:\n{e}')
            self.update_columns()
            self.enable_compare_btn()
            self.update_tab_labels()
            self.view.update_filter_buttons()

    def reload_file2(self) -> None:
        """
        Reload the second CSV file (e.g., after changing delimiter or encoding) and reapply filters.
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
            if self.view.df2 is not None:
                filter_str = self.view.filter2_var.get().strip()
                if filter_str:
                    try:
                        from csvlotte.utils.helpers import sql_where_to_pandas
                        pandas_expr = sql_where_to_pandas(filter_str)
                        try:
                            df = self.view.df2
                            self.view.df2 = self.view.df2.query(pandas_expr, engine="python", local_dict={'df': df})
                        except Exception:
                            df = self.view.df2
                            self.view.df2 = self.view.df2.eval(pandas_expr)
                    except Exception as e:
                        messagebox.showerror('Fehler', f'Filter für Datei 2 ungültig:\n{e}')
            self.update_columns()
            self.enable_compare_btn()
            self.update_tab_labels()
            self.view.update_filter_buttons()

    def show_file_info(self, file_num: int) -> None:
        """
        Display information (size, rows, columns) for the selected CSV file in a message box.
        :param file_num: 1 for file1, 2 for file2
        """
        if file_num == 1:
            file_path = self.view.file1_path
            df = self.view.df1
            title = 'Info Datei 1'
        else:
            file_path = self.view.file2_path
            df = self.view.df2
            title = 'Info Datei 2'
        if file_path and df is not None:
            import os
            try:
                size_kb = os.path.getsize(file_path) / 1024
            except Exception:
                size_kb = 0
            info = f"Datei: {file_path}\nGröße: {size_kb:.1f} kB\nZeilen: {len(df)}\nSpalten: {len(df.columns)}"
            messagebox.showinfo(title, info)

    def open_filter_window(self, file_num: int) -> None:
        """
        Open the filter dialog for the specified CSV file.
        :param file_num: 1 for file1, 2 for file2
        """
        if file_num == 1:
            self.view.open_filter_window(1)
        else:
            self.view.open_filter_window(2)

    def compare_csvs(self) -> None:
        """
        Compare the selected columns from both CSVs, update progress bar, and prepare results for export.
        """
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

    def export_results_button(self) -> None:
        """
        Trigger export dialog for comparison results based on current tab selection.
        """
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

    def update_columns(self) -> None:
        """
        Update available column selections in the view based on loaded DataFrames.
        """
        if self.view.df1 is not None:
            self.view.column_combo1['values'] = list(self.view.df1.columns)
        if self.view.df2 is not None:
            self.view.column_combo2['values'] = list(self.view.df2.columns)
        if hasattr(self.view, 'export_btn'):
            self.view.export_btn.config(state='disabled')

    def enable_compare_btn(self) -> None:
        """
        Enable or disable the compare button based on whether both CSVs are loaded.
        """
        if self.view.df1 is not None and self.view.df2 is not None:
            self.view.compare_btn.config(state='normal')
        else:
            self.view.compare_btn.config(state='disabled')

    def update_tab_labels(self) -> None:
        """
        Update the labels of the result tabs to reflect file names of the loaded CSVs.
        """
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