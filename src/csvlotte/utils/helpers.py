"""
Utility functions for SQL-like WHERE to pandas expression conversion.
"""
import re

def sql_where_to_pandas(query_str: str, df_name: str ="df") -> str:
    """
    Convert a comprehensive SQL-like WHERE condition into a pandas-compatible boolean expression string.

    Supports:
    - Column names with dots (e.g., "col1.col2") using df_name prefix
    - LIKE / NOT LIKE with '%' wildcards (e.g., "col LIKE '%val%'")
    - IN / NOT IN with value lists (e.g., "col IN ('a', 'b')")
    - IS NULL / IS NOT NULL (e.g., "col IS NULL")
    - BETWEEN (e.g., "col BETWEEN 10 AND 20")
    - Standard operators: =, !=, <>, <, >, <=, >=
    - Logical operators: AND, OR, NOT
    - Parentheses for grouping

    Args:
        query_str (str): SQL-like WHERE clause.
        df_name (str): DataFrame name to prefix column names for dot notation support.

    Returns:
        str: Equivalent pandas expression for DataFrame.query().
    """
    def prefix_column_name(col):
        """Prefix column name with @df_name to handle dot notation in pandas.query()."""
        if '.' in col:
            return f"@{df_name}['{col}']"
        return col
    
    def like_to_pandas(match):
        col = prefix_column_name(match.group(1))
        pattern = match.group(2).strip("'")
        if pattern.startswith('%') and pattern.endswith('%'):
            return f"{col}.str.contains('{pattern[1:-1]}', case=False, na=False)"
        elif pattern.startswith('%'):
            return f"{col}.str.lower().str.endswith('{pattern[1:].lower()}', na=False)"
        elif pattern.endswith('%'):
            return f"{col}.str.lower().str.startswith('{pattern[:-1].lower()}', na=False)"
        else:
            return f"{col}.str.lower() == '{pattern.lower()}'"
    
    def not_like_to_pandas(match):
        col = prefix_column_name(match.group(1))
        pattern = match.group(2).strip("'")
        if pattern.startswith('%') and pattern.endswith('%'):
            return f"~{col}.str.contains('{pattern[1:-1]}', case=False, na=False)"
        elif pattern.startswith('%'):
            return f"~{col}.str.lower().str.endswith('{pattern[1:].lower()}', na=False)"
        elif pattern.endswith('%'):
            return f"~{col}.str.lower().str.startswith('{pattern[:-1].lower()}', na=False)"
        else:
            return f"{col}.str.lower() != '{pattern.lower()}'"
    
    def in_to_pandas(match):
        col = prefix_column_name(match.group(1))
        values = match.group(2)
        # Parse values between parentheses, handle quotes
        value_list = re.findall(r"'([^']*)'|(\w+)", values)
        clean_values = [v[0] if v[0] else v[1] for v in value_list]
        formatted_values = [f"'{v}'" for v in clean_values]
        return f"{col}.isin([{', '.join(formatted_values)}])"
    
    def not_in_to_pandas(match):
        col = prefix_column_name(match.group(1))
        values = match.group(2)
        # Parse values between parentheses, handle quotes
        value_list = re.findall(r"'([^']*)'|(\w+)", values)
        clean_values = [v[0] if v[0] else v[1] for v in value_list]
        formatted_values = [f"'{v}'" for v in clean_values]
        return f"~{col}.isin([{', '.join(formatted_values)}])"
    
    def is_null_to_pandas(match):
        col = prefix_column_name(match.group(1))
        return f"{col}.isna()"
    
    def is_not_null_to_pandas(match):
        col = prefix_column_name(match.group(1))
        return f"{col}.notna()"
    
    def between_to_pandas(match):
        col = prefix_column_name(match.group(1))
        val1 = match.group(2)
        val2 = match.group(3)
        return f"({col} >= {val1}) & ({col} <= {val2})"
    
    # Store original for debugging
    original_query = query_str
    
    # Handle column names with dots by updating regex patterns
    # Updated regex pattern to handle column names with dots - more specific to avoid capturing values
    col_pattern = r"([\w\.]+)"
    
    # Handle single = operator FIRST (convert to ==) - preserve quotes
    # First handle quoted strings - be more specific about column names
    query_str = re.sub(r"\b([\w\.]+)\s*=\s*'([^']*)'", lambda m: f"{prefix_column_name(m.group(1))} == '{m.group(2)}'", query_str)
    # Then handle unquoted values - be more specific  
    query_str = re.sub(r"\b([\w\.]+)\s*=\s*(\d+(?:\.\d+)?)\b", lambda m: f"{prefix_column_name(m.group(1))} == {m.group(2)}", query_str)
    query_str = re.sub(r"\b([\w\.]+)\s*=\s*([a-zA-Z_]\w*)\b", lambda m: f"{prefix_column_name(m.group(1))} == {m.group(2)}", query_str)
    
    # Handle BETWEEN
    query_str = re.sub(r"\b([\w\.]+)\s+BETWEEN\s+(\d+\.?\d*)\s+AND\s+(\d+\.?\d*)", 
                      between_to_pandas, query_str, flags=re.IGNORECASE)
    
    # Handle IS NOT NULL
    query_str = re.sub(r"\b([\w\.]+)\s+IS\s+NOT\s+NULL", 
                      is_not_null_to_pandas, query_str, flags=re.IGNORECASE)
    
    # Handle IS NULL
    query_str = re.sub(r"\b([\w\.]+)\s+IS\s+NULL", 
                      is_null_to_pandas, query_str, flags=re.IGNORECASE)
    
    # Handle NOT IN
    query_str = re.sub(r"\b([\w\.]+)\s+NOT\s+IN\s+\(([^)]+)\)", 
                      not_in_to_pandas, query_str, flags=re.IGNORECASE)
    
    # Handle IN
    query_str = re.sub(r"\b([\w\.]+)\s+IN\s+\(([^)]+)\)", 
                      in_to_pandas, query_str, flags=re.IGNORECASE)
    
    # Handle NOT LIKE
    query_str = re.sub(r"\b([\w\.]+)\s+NOT\s+LIKE\s+'([^']+)'", 
                      not_like_to_pandas, query_str, flags=re.IGNORECASE)
    
    # Handle LIKE
    query_str = re.sub(r"\b([\w\.]+)\s+LIKE\s+'([^']+)'", 
                      like_to_pandas, query_str, flags=re.IGNORECASE)
    
    # Handle <> operator (convert to !=)
    query_str = re.sub(r'<>', '!=', query_str)
    
    # Handle NOT operator (convert to ~) - updated to handle prefixed columns
    query_str = re.sub(r'\bNOT\s+([\w\.]+)', lambda m: f'~{prefix_column_name(m.group(1))}', query_str, flags=re.IGNORECASE)
    
    # Handle AND/OR operators
    query_str = re.sub(r'\bAND\b', '&', query_str, flags=re.IGNORECASE)
    query_str = re.sub(r'\bOR\b', '|', query_str, flags=re.IGNORECASE)
    
    # Handle remaining column references for comparison operators
    # This handles cases like "col1.col2 > 5" that weren't caught by the = operator
    query_str = re.sub(r'\b([\w\.]+)(?=\s*[<>!=]+)', lambda m: prefix_column_name(m.group(1)), query_str)
    
    return query_str
