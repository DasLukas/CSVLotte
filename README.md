# CSVLotte

CSVLotte is a graphical Python tool for comparing, filtering, and exporting CSV files.

## Features
- **Compare two CSV files** (intersections, differences, etc.)
- **SQL-like filters** for both files
- **Column selection and slicing**
- **Export comparison results**
- **Multilingual interface** (German/English)
- **User-friendly modern GUI (Tkinter)**

## Installation

1. Install Python 3.11+
2. Clone or extract the repository
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   or with Poetry:
   ```bash
   poetry install
   ```

## Start

```bash
python -m src.main
```

## Usage
1. Select CSV files
2. Optionally set filters (SQL WHERE)
3. Select columns to compare
4. Optionally slice the column content
5. Start comparison
6. View and export results in tabs

## Example Filters

You can use SQL-like WHERE clauses to filter your CSV data before comparison. Here are some examples:

- **Select all rows where column 'age' is greater than 30:**
  ```sql
  age > 30
  ```
- **Select rows where column 'country' is Germany:**
  ```sql
  country = 'Germany'
  ```
- **Select rows where column 'status' is not 'active':**
  ```sql
  status != 'active'
  ```
- **Select rows where column 'score' is between 50 and 100:**
  ```sql
  score >= 50 AND score <= 100
  ```
- **Select rows where column 'name' starts with 'A':**
  ```sql
  name LIKE 'A%'
  ```
- **Select rows where column 'date' is after 2024-01-01:**
  ```sql
  date > '2024-01-01'
  ```
- **Combine multiple conditions:**
  ```sql
  country = 'USA' AND (age < 18 OR status = 'student')
  ```
- **Select rows where column 'user.id' equals 42:**
  ```sql
  user.id = 42
  ```

You can use operators like `=`, `!=`, `>`, `<`, `>=`, `<=`, `AND`, `OR`, and `LIKE` (for string patterns). String values must be in single quotes.

Add your filter in the filter field for each CSV file as needed before starting the comparison.

## Example Column Slicing

You can use Python-like slice syntax to compare only parts of a column's content. Enter the slice in the corresponding field next to the column selection.

- **Compare only the first 5 characters:**
  ```
  :5
  ```
- **Compare characters 3 to 7 (zero-based, end exclusive):**
  ```
  3:7
  ```
- **Compare the last 4 characters:**
  ```
  -4:
  ```
- **Compare every second character:**
  ```
  ::2
  ```
- **Compare from character 2 to the end:**
  ```
  2:
  ```

The syntax follows Python's `[start:stop:step]` convention. Leave the field empty to use the full column content.

## Change Language
- Use the menu **File → Settings** to change the language (restart required).

## License
MIT License

---

**Developed with ❤️ in Python.**
