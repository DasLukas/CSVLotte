"""
Utility functions for SQL-like WHERE to pandas expression conversion.
"""
import re

def sql_where_to_pandas(query_str: str) -> str:
    """
    Convert a comprehensive SQL-like WHERE condition into a pandas-compatible boolean expression string.

    Supports:
    - LIKE / NOT LIKE with '%' wildcards (e.g., "col LIKE '%val%'")
    - IN / NOT IN with value lists (e.g., "col IN ('a', 'b')")
    - IS NULL / IS NOT NULL (e.g., "col IS NULL")
    - BETWEEN (e.g., "col BETWEEN 10 AND 20")
    - Standard operators: =, !=, <>, <, >, <=, >=
    - Logical operators: AND, OR, NOT
    - Parentheses for grouping

    Args:
        query_str (str): SQL-like WHERE clause.

    Returns:
        str: Equivalent pandas expression for DataFrame.query().
    """
    def like_to_pandas(match):
        col = match.group(1)
        pattern = match.group(2).strip("'")
        if pattern.startswith('%') and pattern.endswith('%'):
            return f"{col}.str.contains('{pattern[1:-1]}', na=False)"
        elif pattern.startswith('%'):
            return f"{col}.str.endswith('{pattern[1:]}', na=False)"
        elif pattern.endswith('%'):
            return f"{col}.str.startswith('{pattern[:-1]}', na=False)"
        else:
            return f"{col} == '{pattern}'"
    # LIKE-Ausdrücke ersetzen
    query_str = re.sub(r"(\w+)\s+LIKE\s+'([^']+)'", like_to_pandas, query_str, flags=re.IGNORECASE)
    # AND/OR in Python-Operatoren umwandeln
    query_str = re.sub(r'\bAND\b', '&', query_str, flags=re.IGNORECASE)
    query_str = re.sub(r'\bOR\b', '|', query_str, flags=re.IGNORECASE)
    return query_str
