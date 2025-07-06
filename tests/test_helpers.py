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
    
    def test_logical_operators(self):
        """Test AND and OR logical operators."""
        # Test AND operator
        query = "age > 25 AND department LIKE 'IT'"
        result = sql_where_to_pandas(query)
        expected = "age > 25 & department.str.lower() == 'it'"
        assert result == expected
        
        filtered = self.df.query(result)
        assert len(filtered) == 2  # Charlie and the unnamed person
        
        # Test OR operator
        query = "city LIKE 'Berlin' OR salary > 70000"
        result = sql_where_to_pandas(query)
        expected = "city.str.lower() == 'berlin' | salary > 70000"
        assert result == expected
        
        filtered = self.df.query(result)
        assert len(filtered) == 3  # Two Berlin entries + one high salary
        
        # Test mixed AND/OR
        query = "department LIKE 'IT' AND age > 30 OR salary > 75000"
        result = sql_where_to_pandas(query)
        expected = "department.str.lower() == 'it' & age > 30 | salary > 75000"
        assert result == expected
    
    def test_case_insensitive_keywords(self):
        """Test that SQL keywords work in different cases."""
        # Test lowercase
        query = "name like '%a%' and age > 25"
        result = sql_where_to_pandas(query)
        expected = "name.str.contains('a', case=False, na=False) & age > 25"
        assert result == expected
        
        # Test mixed case
        query = "city Like 'Ber%' Or salary > 60000"
        result = sql_where_to_pandas(query)
        expected = "city.str.lower().str.startswith('ber', na=False) | salary > 60000"
        assert result == expected
        
        # Test uppercase
        query = "department LIKE '%T%' AND city LIKE 'Berlin'"
        result = sql_where_to_pandas(query)
        expected = "department.str.contains('T', case=False, na=False) & city.str.lower() == 'berlin'"
        assert result == expected
    
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
        assert result == "salary = 50000"
    
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
