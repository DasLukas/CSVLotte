import pandas as pd

class FilterController:

    def get_filtered(self):
        """
        Gibt den aktuell gefilterten DataFrame zurück.
        """
        return self.df_filtered
    """
    Controller für die Filter-Dialog-Logik. Kapselt das Anwenden von SQL-ähnlichen Filtern auf DataFrames
    und die Aktualisierung der angezeigten Tabelle im Filter-Dialog.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.df_filtered = df

    def apply_filter(self, filter_str: str) -> pd.DataFrame:
        """
        Wendet den gegebenen Filter-String (WHERE SQL) auf den DataFrame an.
        Gibt den gefilterten DataFrame zurück. Bei Fehlern wird der ungefilterte DataFrame zurückgegeben.
        """
        if self.df is None or self.df.empty or not filter_str:
            self.df_filtered = self.df
            return self.df
        try:
            from csvlotte.utils.helpers import sql_where_to_pandas
            pandas_expr = sql_where_to_pandas(filter_str)
            # Versuche zuerst mit query, dann mit eval falls nötig
            try:
                self.df_filtered = self.df.query(pandas_expr, engine="python")
            except Exception:
                self.df_filtered = self.df.eval(pandas_expr)
        except Exception:
            self.df_filtered = self.df
        return self.df_filtered

    def get_columns(self):
        if self.df_filtered is not None and not self.df_filtered.empty:
            return list(self.df_filtered.columns)
        return []

    def get_rows(self):
        if self.df_filtered is not None and not self.df_filtered.empty:
            return self.df_filtered.values.tolist()
        return []

    def export_filtered(self, path, sep=';', encoding='latin1'):
        if self.df_filtered is not None and not self.df_filtered.empty:
            self.df_filtered.to_csv(path, sep=sep, encoding=encoding, index=False)
            return True
        return False
