from csvlotte.views.compare_export_view import CompareExportView
import os
from typing import Any, List, Optional, Tuple

class CompareExportController:
    def __init__(self, parent: Any, dfs: List[Any], result_table_labels: List[str], current_tab: int = 0, default_dir: Optional[str] = None) -> None:
        self.parent = parent
        self.dfs = dfs  # Liste der Ergebnis-DataFrames (z.B. [df_only1, df_common1, df_only2])
        self.result_table_labels = result_table_labels
        self.current_tab = current_tab
        self.default_dir = default_dir

    def open_export_dialog(self) -> None:
        # Bestimme den aktuellen Tab und zugehörigen DataFrame
        df = self.dfs[self.current_tab] if self.dfs and self.dfs[self.current_tab] is not None else None
        if df is None or df.empty:
            from tkinter import messagebox
            messagebox.showerror('Fehler', 'Kein Ergebnis zum Exportieren!')
            return
        CompareExportView(self.parent, self, self.dfs, self.result_table_labels, self.current_tab, self.default_dir)

    def export_result(self, idx: int, exclude_columns: Optional[List[str]], out_path: str, sep: str = ';', encoding: str = 'latin1') -> Tuple[bool, Optional[str]]:
        try:
            df_export = self.dfs[idx]
            if exclude_columns:
                df_export = df_export.drop(columns=exclude_columns)
            df_export.to_csv(out_path, sep=sep, encoding=encoding, index=False)
            return True, None
        except Exception as e:
            return False, str(e)
