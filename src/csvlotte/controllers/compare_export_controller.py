
from csvlotte.views.compare_export_view import CompareExportView
import os

class CompareExportController:
    def __init__(self, parent, dfs, result_table_labels, current_tab=0, default_dir=None):
        self.parent = parent
        self.dfs = dfs  # Liste der Ergebnis-DataFrames (z.B. [df_only1, df_common1, df_only2])
        self.result_table_labels = result_table_labels
        self.current_tab = current_tab
        self.default_dir = default_dir

    def open_export_dialog(self):
        # Bestimme den aktuellen Tab und zugehörigen DataFrame
        df = self.dfs[self.current_tab] if self.dfs and self.dfs[self.current_tab] is not None else None
        if df is None or df.empty:
            from tkinter import messagebox
            messagebox.showerror('Fehler', 'Kein Ergebnis zum Exportieren!')
            return
        CompareExportView(self.parent, self, self.dfs, self.result_table_labels, self.current_tab, self.default_dir)

    def export_result(self, idx, exclude_columns, out_path, sep=';', encoding='latin1'):
        try:
            df_export = self.dfs[idx]
            if exclude_columns:
                df_export = df_export.drop(columns=exclude_columns)
            df_export.to_csv(out_path, sep=sep, encoding=encoding, index=False)
            return True, None
        except Exception as e:
            return False, str(e)
