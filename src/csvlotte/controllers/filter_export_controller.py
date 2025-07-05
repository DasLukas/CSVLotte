from csvlotte.views.filter_export_view import FilterExportView

class FilterExportController:
    def __init__(self, parent, df, source_path=None, default_dir=None, default_name=None):
        self.parent = parent
        self.df = df
        self.source_path = source_path
        self.default_dir = default_dir
        self.default_name = default_name

    def open_export_dialog(self):
        if self.df is None or self.df.empty:
            from tkinter import messagebox
            messagebox.showerror('Fehler', 'Keine Daten zum Exportieren!')
            return
        # Ermittle Speicherort und Namen anhand des Ursprungsdateipfads
        # self.source_path sollte der Pfad der Original-CSV sein
        # Reiche source_path explizit als default_dir UND source_path weiter, damit der View es sicher nutzt
        default_dir = None
        default_name = None
        if self.source_path:
            import os
            default_dir = os.path.dirname(self.source_path)
            base, ext = os.path.splitext(os.path.basename(self.source_path))
            default_name = f"{base}_filtered{ext}"
        FilterExportView(self.parent, self.df, default_dir=default_dir, default_name=default_name, source_path=self.source_path)
