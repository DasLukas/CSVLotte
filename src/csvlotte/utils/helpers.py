# --- SQL-ähnliche WHERE-zu-Pandas-Logik (aus sqlfilter.py) ---
import re

def sql_where_to_pandas(query_str):
    """
    Wandelt eine SQL-ähnliche WHERE-Bedingung mit LIKE, AND, OR in einen Pandas-kompatiblen Ausdruck um.
    Gibt einen String zurück, der mit df.eval() verwendet werden kann.
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
