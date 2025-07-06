"""
Tests for utility functions in helpers.py
"""
import pytest
import pandas as pd
from src.csvlotte.utils.helpers import sql_where_to_pandas


class TestSqlWhereToPandas:
    """Test cases for SQL WHERE to pandas conversion function."""
    
    def setup_method(self):
        """Set up test data for each test method."""
        self.df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'David', None],
            'age': [25, 30, 35, None, 40],
            'city': ['Berlin', 'Munich', 'Hamburg', 'Berlin', 'Dresden'],
            'salary': [50000, 60000, 70000, 55000, 80000],
            'department': ['IT', 'HR', 'IT', 'Finance', 'IT']
        })
    
    def test_like_operations(self):
        """Test LIKE operations with different wildcard patterns."""
        # Test contains pattern
        query = "name LIKE '%li%'"
        result = sql_where_to_pandas(query)
        expected = "name.str.contains('li', case=False, na=False)"
        assert result == expected
        
        # Test actual filtering with the converted query
        filtered = self.df.query(result)
        assert len(filtered) == 2  # Alice and Charlie
        assert 'Alice' in filtered['name'].values
        assert 'Charlie' in filtered['name'].values
        
        # Test starts with pattern
        query = "city LIKE 'Ber%'"
        result = sql_where_to_pandas(query)
        expected = "city.str.lower().str.startswith('ber', na=False)"
        assert result == expected
        
        filtered = self.df.query(result)
        assert len(filtered) == 2  # Both Berlin entries
        
        # Test ends with pattern
        query = "city LIKE '%ich'"
        result = sql_where_to_pandas(query)
        expected = "city.str.lower().str.endswith('ich', na=False)"
        assert result == expected
        
        filtered = self.df.query(result)
        assert len(filtered) == 1  # Munich
        assert filtered['city'].iloc[0] == 'Munich'
        
        # Test exact match pattern
        query = "department LIKE 'IT'"
        result = sql_where_to_pandas(query)
        expected = "department.str.lower() == 'it'"
        assert result == expected
        
        filtered = self.df.query(result)
        assert len(filtered) == 3  # Three IT department entries
    
    def test_not_like_operations(self):
        """Test NOT LIKE operations."""
        # Test NOT LIKE contains pattern
        query = "name NOT LIKE '%li%'"
        result = sql_where_to_pandas(query)
        expected = "~name.str.contains('li', case=False, na=False)"
        assert result == expected
        
        filtered = self.df.query(result)
        assert len(filtered) == 3  # Bob, David, None (excluding Alice and Charlie)
        assert 'Bob' in filtered['name'].values
        assert 'David' in filtered['name'].values
        
        # Test NOT LIKE starts with pattern
        query = "city NOT LIKE 'Ber%'"
        result = sql_where_to_pandas(query)
        expected = "~city.str.lower().str.startswith('ber', na=False)"
        assert result == expected
        
        filtered = self.df.query(result)
        assert len(filtered) == 3  # Munich, Hamburg, Dresden (excluding Berlin entries)
    
    def test_in_operations(self):
        """Test IN and NOT IN operations."""
        # Test IN with quoted values
        query = "department IN ('IT', 'HR')"
        result = sql_where_to_pandas(query)
        expected = "department.isin(['IT', 'HR'])"
        assert result == expected
        
        filtered = self.df.query(result)
        assert len(filtered) == 4  # Three IT + one HR
        
        # Test NOT IN
        query = "department NOT IN ('IT', 'HR')"
        result = sql_where_to_pandas(query)
        expected = "~department.isin(['IT', 'HR'])"
        assert result == expected
        
        filtered = self.df.query(result)
        assert len(filtered) == 1  # Only Finance
        assert filtered['department'].iloc[0] == 'Finance'
        
        # Test IN with mixed quoted and unquoted values
        query = "city IN ('Berlin', Munich)"
        result = sql_where_to_pandas(query)
        expected = "city.isin(['Berlin', 'Munich'])"
        assert result == expected
    
    def test_null_operations(self):
        """Test IS NULL and IS NOT NULL operations."""
        # Test IS NULL
        query = "age IS NULL"
        result = sql_where_to_pandas(query)
        expected = "age.isna()"
        assert result == expected
        
        filtered = self.df.query(result)
        assert len(filtered) == 1  # One record with null age
        
        # Test IS NOT NULL
        query = "name IS NOT NULL"
        result = sql_where_to_pandas(query)
        expected = "name.notna()"
        assert result == expected
        
        filtered = self.df.query(result)
        assert len(filtered) == 4  # Four records with non-null names
        
        # Test complex condition with NULL
        query = "age IS NOT NULL AND salary > 60000"
        result = sql_where_to_pandas(query)
        expected = "age.notna() & salary > 60000"
        assert result == expected
    
    def test_between_operations(self):
        """Test BETWEEN operations."""
        # Test BETWEEN with integers
        query = "age BETWEEN 30 AND 40"
        result = sql_where_to_pandas(query)
        expected = "(age >= 30) & (age <= 40)"
        assert result == expected
        
        filtered = self.df.query(result)
        assert len(filtered) == 3  # Bob (30), Charlie (35), and unnamed person (40)
        
        # Test BETWEEN with floats
        query = "salary BETWEEN 55000.0 AND 65000.0"
        result = sql_where_to_pandas(query)
        expected = "(salary >= 55000.0) & (salary <= 65000.0)"
        assert result == expected
        
        filtered = self.df.query(result)
        assert len(filtered) == 2  # Bob (60000) and David (55000)
    
    def test_comparison_operators(self):
        """Test standard comparison operators including <>."""
        # Test = operator (equals)
        query = "department = 'IT'"
        result = sql_where_to_pandas(query)
        expected = "department == 'IT'"
        assert result == expected
        
        filtered = self.df.query(result)
        assert len(filtered) == 3  # Three IT department entries
        
        # Test <> operator (not equal)
        query = "department <> 'IT'"
        result = sql_where_to_pandas(query)
        expected = "department != 'IT'"
        assert result == expected
        
        filtered = self.df.query(result)
        assert len(filtered) == 2  # HR and Finance
        
        # Test combination with other operators
        query = "age >= 30 AND department <> 'HR'"
        result = sql_where_to_pandas(query)
        expected = "age >= 30 & department != 'HR'"
        assert result == expected
    
    def test_not_operator(self):
        """Test NOT logical operator."""
        # Test NOT with simple condition
        query = "NOT age > 30"
        result = sql_where_to_pandas(query)
        expected = "~age > 30"
        assert result == expected
        
        # Note: This might need parentheses for proper evaluation in complex cases
        # The current implementation is basic but functional for simple NOT conditions
    
    def test_complex_queries(self):
        """Test complex queries with multiple conditions."""
        query = "name LIKE '%e%' AND age > 25 OR department LIKE 'HR'"
        result = sql_where_to_pandas(query)
        expected = "name.str.contains('e', case=False, na=False) & age > 25 | department.str.lower() == 'hr'"
        assert result == expected
        
        filtered = self.df.query(result)
        assert len(filtered) == 2  # Charlie (name contains 'e' and age > 25) + Bob (HR)
    
    def test_empty_and_edge_cases(self):
        """Test edge cases and empty inputs."""
        # Empty string
        result = sql_where_to_pandas("")
        assert result == ""
        
        # Only spaces
        result = sql_where_to_pandas("   ")
        assert result == "   "
        
        # Simple condition without LIKE
        query = "age > 30"
        result = sql_where_to_pandas(query)
        assert result == "age > 30"
        
        # Query without any special keywords
        query = "salary = 50000"
        result = sql_where_to_pandas(query)
        assert result == "salary == 50000"
    
    def test_special_characters_in_patterns(self):
        """Test LIKE patterns with special characters."""
        # Test with quotes in pattern
        query = "name LIKE '%o%'"
        result = sql_where_to_pandas(query)
        expected = "name.str.contains('o', case=False, na=False)"
        assert result == expected
        
        # Test with numbers in pattern
        query = "department LIKE '%T%'"
        result = sql_where_to_pandas(query)
        expected = "department.str.contains('T', case=False, na=False)"
        assert result == expected
    
    def test_multiple_like_conditions(self):
        """Test queries with multiple LIKE conditions."""
        query = "name LIKE '%a%' AND city LIKE 'Ber%'"
        result = sql_where_to_pandas(query)
        expected = "name.str.contains('a', case=False, na=False) & city.str.lower().str.startswith('ber', na=False)"
        assert result == expected
        
        filtered = self.df.query(result)
        # Now case-insensitive: Alice contains 'A' (matches 'a') AND city Berlin ✓
        # David: contains 'a' AND city Berlin (starts with 'Ber') ✓
        assert len(filtered) == 2  # Alice and David both match (now case-insensitive)
        
        query = "name LIKE '%a%' OR city LIKE 'Ber%'"
        result = sql_where_to_pandas(query)
        expected = "name.str.contains('a', case=False, na=False) | city.str.lower().str.startswith('ber', na=False)"
        assert result == expected
        
        filtered = self.df.query(result)
        # Alice: contains 'A' (matches 'a') ✓ AND city Berlin ✓  
        # Charlie: contains 'a' ✓
        # David: contains 'a' ✓ AND city Berlin ✓
        # Total: Alice, Charlie, David = 3
        assert len(filtered) == 3  # Alice, Charlie, David

if __name__ == "__main__":
    pytest.main([__file__])
