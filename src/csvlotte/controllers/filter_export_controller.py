"""
Module for FilterExportController: handles exporting filtered CSV data.
"""

from csvlotte.views.filter_export_view import FilterExportView
from typing import Any, Optional, Tuple
import os
import pandas as pd

class FilterExportController:
    """
    Controller to manage exporting of filtered DataFrame to CSV files.
    """
    def __init__(self, parent: Any, df: pd.DataFrame, source_path: Optional[str] = None, default_dir: Optional[str] = None, default_name: Optional[str] = None) -> None:
        """
        Initialize the export controller with GUI parent and DataFrame.

        Args:
            parent (Any): Parent GUI window.
            df (pd.DataFrame): DataFrame to export.
            source_path (Optional[str]): Path of source CSV file.
            default_dir (Optional[str]): Default directory for export.
            default_name (Optional[str]): Default filename for export.
        """
        self.parent = parent
        self.df = df
        self.source_path = source_path
        self.default_dir = default_dir
        self.default_name = default_name

    def open_export_dialog(self) -> None:
        """
        Open the export dialog for the user to select options.
        """
        if self.df is None or self.df.empty:
            from tkinter import messagebox
            messagebox.showerror('Fehler', 'Keine Daten zum Exportieren!')
            return
        # Ermittle Speicherort und Namen anhand des Ursprungsdateipfads
        default_dir = None
        default_name = None
        if self.source_path:
            default_dir = os.path.dirname(self.source_path)
            base, ext = os.path.splitext(os.path.basename(self.source_path))
            default_name = f"{base}_filtered{ext}"
        FilterExportView(self.parent, self, default_dir=default_dir, default_name=default_name, source_path=self.source_path)

    def export_filtered(self, out_path: str, sep: str = ';', encoding: str = 'latin1') -> Tuple[bool, Optional[str]]:
        """
        Export the DataFrame to the specified CSV file.

        Args:
            out_path (str): Output file path.
            sep (str): CSV field separator.
            encoding (str): File encoding.

        Returns:
            Tuple[bool, Optional[str]]: (success flag, error message if failed).
        """
        try:
            self.df.to_csv(out_path, sep=sep, encoding=encoding, index=False)
            return True, None
        except Exception as e:
            return False, str(e)
