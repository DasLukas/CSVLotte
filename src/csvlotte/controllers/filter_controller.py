"""
Module for filtering DataFrames using SQL-like WHERE conditions and exporting filtered results.
"""
import pandas as pd
from typing import List, Optional, Any

class FilterController:
    """
    Controller to apply SQL-like filter expressions to a pandas DataFrame and manage the filtered data.
    """

    def get_filtered(self) -> pd.DataFrame:
        """
        Return the currently filtered DataFrame.

        Returns:
            pd.DataFrame: The filtered DataFrame (might be original DataFrame if no filter applied).
        """
        return self.df_filtered
    def __init__(self, df: pd.DataFrame) -> None:
        """
        Initialize the FilterController with the given DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame to be filtered.
        """
        self.df = df
        self.df_filtered = df

    def apply_filter(self, filter_str: str) -> pd.DataFrame:
        """
        Apply a SQL-like WHERE filter string to the DataFrame.

        Args:
            filter_str (str): SQL-like WHERE condition (e.g., "col1 = 'value' AND col2 > 10").

        Returns:
            pd.DataFrame: The filtered DataFrame. On error, returns the original DataFrame.
        """
        if self.df is None or self.df.empty or not filter_str:
            self.df_filtered = self.df
            return self.df
        try:
            from csvlotte.utils.helpers import sql_where_to_pandas
            pandas_expr = sql_where_to_pandas(filter_str)
            # Use only query() for filtering - never eval() to avoid assignment operations
            # Make DataFrame available as 'df' for @df references in query
            df = self.df
            self.df_filtered = self.df.query(pandas_expr, engine="python", local_dict={'df': df})
        except Exception as e:
            # Log the error for debugging purposes
            print(f"Filter error: {e}")
            # Return original DataFrame on any error
            self.df_filtered = self.df
        return self.df_filtered

    def get_columns(self) -> List[str]:
        """
        Get the column names of the filtered DataFrame or an empty list.

        Returns:
            List[str]: List of column names if data exists, otherwise empty.
        """
        if self.df_filtered is not None and not self.df_filtered.empty:
            return list(self.df_filtered.columns)
        return []

    def get_rows(self) -> List[List[Any]]:
        """
        Get the row data of the filtered DataFrame as a list of records.

        Returns:
            List[List[Any]]: List of rows, where each row is a list of values.
        """
        if self.df_filtered is not None and not self.df_filtered.empty:
            return self.df_filtered.values.tolist()
        return []

    def export_filtered(self, path: str, sep: str = ';', encoding: str = 'latin1') -> bool:
        """
        Export the filtered DataFrame to a CSV file.

        Args:
            path (str): Output file path for the CSV.
            sep (str, optional): Field separator. Defaults to ';'.
            encoding (str, optional): File encoding. Defaults to 'latin1'.

        Returns:
            bool: True if export succeeded, False otherwise.
        """
        if self.df_filtered is not None and not self.df_filtered.empty:
            self.df_filtered.to_csv(path, sep=sep, encoding=encoding, index=False)
            return True
        return False
