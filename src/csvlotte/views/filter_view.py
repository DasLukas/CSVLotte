
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ..controllers.filter_controller import FilterController

class FilterView(tk.Toplevel):
    def __init__(self, parent, df, var, title, apply_callback=None, source_path=None):
        super().__init__(parent)
        self.title(title)
        self.grab_set()
        self.resizable(True, True)
        self.var = var
        self.apply_callback = apply_callback
        self.controller = FilterController(df)
        self.source_path = source_path
        # Setze Fenstergröße auf 2/3 der Bildschirmgröße
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        width = int(screen_w * 2 / 3)
        height = int(screen_h * 2 / 3)
        x = (screen_w // 2) - (width // 2)
        y = (screen_h // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self._build_widgets()

    def _build_widgets(self):
        # Tabelle oben (mit Scrollbars direkt am Widget)
        table_frame = tk.Frame(self)
        table_frame.pack(fill='both', expand=True, side='top', padx=10, pady=(10, 2))
        self.tree = ttk.Treeview(table_frame, show='headings')
        self.tree.grid(row=0, column=0, sticky='nsew')
        xscroll = ttk.Scrollbar(table_frame, orient='horizontal', command=self.tree.xview)
        xscroll.grid(row=1, column=0, sticky='ew')
        self.tree.configure(xscrollcommand=xscroll.set)
        yscroll = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        yscroll.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=yscroll.set)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        # Filtereingabe und Buttons unten
        bottom_frame = tk.Frame(self)
        bottom_frame.pack(side='bottom', fill='x', padx=10, pady=10)
        tk.Label(bottom_frame, text='Filter:').pack(side='left', padx=(0, 5))
        self.text = tk.Text(bottom_frame, height=1)
        self.text.pack(side='left', padx=(0, 5), fill='x', expand=True)
        self.text.insert('1.0', self.var.get())
        btn_frame = tk.Frame(bottom_frame)
        btn_frame.pack(side='left', padx=5)
        tk.Button(btn_frame, text='Übernehmen', command=self._apply_and_update).pack(side='left', padx=5)
        tk.Button(btn_frame, text='Exportieren', command=self._export_filtered).pack(side='left', padx=5)
        tk.Button(btn_frame, text='Schließen', command=self.destroy).pack(side='left', padx=5)
        self._populate_table()

    def _populate_table(self):
        df = self.controller.get_filtered()
        self.tree.delete(*self.tree.get_children())
        if df is not None and not df.empty:
            cols = list(df.columns)
            self.tree['columns'] = cols
            for col in cols:
                self.tree.heading(col, text=col)
            for _, row in df.iterrows():
                self.tree.insert('', 'end', values=list(row))
        else:
            self.tree['columns'] = []

    def _apply_and_update(self):
        filter_str = self.text.get('1.0', 'end').strip()
        self.var.set(filter_str)
        df_filtered = self.controller.apply_filter(filter_str)
        if df_filtered is None:
            messagebox.showerror('Fehler', 'Filter konnte nicht angewendet werden. Bitte prüfen Sie die Syntax.')
            return
        self._populate_table()
        if self.apply_callback:
            self.apply_callback(filter_str)

    def _export_filtered(self):
        from csvlotte.controllers.filter_export_controller import FilterExportController
        df = self.controller.get_filtered()
        if df is None or df.empty:
            messagebox.showerror('Fehler', 'Keine Daten zum Exportieren!')
            return
        # Nutze den übergebenen source_path, falls vorhanden, ansonsten wie bisher fallback
        source_path = self.source_path
        if not source_path:
            # Prüfe, ob das Ursprungs-DataFrame identisch mit df1 oder df2 im Hauptfenster ist
            if hasattr(self.master, 'df1') and self.master.df1 is not None and self.controller.df is self.master.df1:
                source_path = getattr(self.master, 'file1_path', None)
            elif hasattr(self.master, 'df2') and self.master.df2 is not None and self.controller.df is self.master.df2:
                source_path = getattr(self.master, 'file2_path', None)
            # Fallback: falls nicht eindeutig, nimm file1_path, falls vorhanden
            if not source_path and hasattr(self.master, 'file1_path'):
                source_path = getattr(self.master, 'file1_path', None)
        FilterExportController(self, df, source_path=source_path).open_export_dialog()
