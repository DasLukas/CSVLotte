"""
Module for CompareExportController: handles exporting comparison results to CSV files.
"""

from csvlotte.views.compare_export_view import CompareExportView
from typing import Any, List, Optional, Tuple

class CompareExportController:
    """
    Controller to manage exporting of comparison result DataFrames.
    """
    def __init__(self, parent: Any, dfs: List[Any], result_table_labels: List[str], current_tab: int = 0, default_dir: Optional[str] = None) -> None:
        """
        Initialize the export controller with parent window and data.

        Args:
            parent (Any): The parent GUI window.
            dfs (List[Any]): List of DataFrames to export.
            result_table_labels (List[str]): Labels for each result tab.
            current_tab (int): Index of the currently selected tab.
            default_dir (Optional[str]): Default directory for export.
        """
        self.parent = parent
        self.dfs = dfs
        self.result_table_labels = result_table_labels
        self.current_tab = current_tab
        self.default_dir = default_dir

    def open_export_dialog(self) -> None:
        """
        Open the export dialog window for user to select export options.
        """
        # Bestimme den aktuellen Tab und zugehörigen DataFrame
        df = self.dfs[self.current_tab] if self.dfs and self.dfs[self.current_tab] is not None else None
        if df is None or df.empty:
            from tkinter import messagebox
            messagebox.showerror('Fehler', 'Kein Ergebnis zum Exportieren!')
            return
        CompareExportView(self.parent, self, self.dfs, self.result_table_labels, self.current_tab, self.default_dir)

    def export_result(self, idx: int, exclude_columns: Optional[List[str]], out_path: str, sep: str = ';', encoding: str = 'latin1') -> Tuple[bool, Optional[str]]:
        """
        Export the selected DataFrame to a CSV file.

        Args:
            idx (int): Index of the DataFrame to export.
            exclude_columns (Optional[List[str]]): Columns to exclude.
            out_path (str): Path to save the CSV file.
            sep (str, optional): CSV separator. Defaults to ';'.
            encoding (str, optional): File encoding. Defaults to 'latin1'.

        Returns:
            Tuple[bool, Optional[str]]: (success flag, error message if failed).
        """
        try:
            df_export = self.dfs[idx]
            if exclude_columns:
                df_export = df_export.drop(columns=exclude_columns)
            df_export.to_csv(out_path, sep=sep, encoding=encoding, index=False)
            return True, None
        except Exception as e:
            return False, str(e)
