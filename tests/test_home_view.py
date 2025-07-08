"""
Tests for HomeView class - focusing on business logic only.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from csvlotte.views.home_view import HomeView


class TestHomeViewBusinessLogic:
    """Test cases for HomeView business logic methods."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        # Mock Tkinter completely to avoid GUI initialization
        self.mock_root = Mock()
        self.mock_controller = Mock()
        
        # Create test DataFrames
        self.test_df1 = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35],
            'city': ['Berlin', 'Munich', 'Hamburg']
        })
        
        self.test_df2 = pd.DataFrame({
            'name': ['Bob', 'David', 'Eve'],
            'age': [30, 28, 32],
            'country': ['Germany', 'USA', 'France']
        })
        
        # Mock all GUI components and create view without actual GUI
        with patch.multiple(
            'csvlotte.views.home_view',
            tk=Mock(),
            ttk=Mock(),
            messagebox=Mock(),
            filedialog=Mock()
        ), patch.object(HomeView, '_build_ui'), patch.object(HomeView, '_set_icon'):
            self.view = HomeView(self.mock_root, self.mock_controller)
            
        # Manually set up the minimal attributes needed for testing
        self._setup_minimal_view_attributes()
    
    def teardown_method(self):
        """Clean up after each test."""
        # No cleanup needed since we're not using real Tkinter
        pass
    
    def _setup_minimal_view_attributes(self):
        """Setup minimal view attributes needed for business logic tests."""
        # DataFrames
        self.view.df1 = None
        self.view.df2 = None
        self.view._result_dfs = [None, None, None, None]
        
        # File paths
        self.view.file1_path = None
        self.view.file2_path = None
        
        # Mock UI components
        self.view.column_combo1 = Mock()
        self.view.column_combo2 = Mock()
        self.view.filter1_btn = Mock()
        self.view.filter2_btn = Mock()
        self.view.filter1_var = Mock()
        self.view.filter2_var = Mock()
        
        # Mock result tables
        self.view.result_tables = [Mock(), Mock(), Mock(), Mock()]
        for i, table in enumerate(self.view.result_tables):
            table.delete = Mock()
            table.get_children = Mock(return_value=[])
            table.__setitem__ = Mock()
            table.heading = Mock()
            table.column = Mock()
            table.insert = Mock()
        
        # Initialize sort states
        self.view._sort_states = [{} for _ in range(4)]
    
    # Tests for update_result_table_view method
    def test_update_result_table_view_with_data(self):
        """Test updating result table view with valid DataFrames."""
        # Arrange
        self.view._result_dfs = [
            self.test_df1.copy(),
            self.test_df2.copy(), 
            None,
            pd.DataFrame()  # Empty DataFrame
        ]
        
        # Act
        self.view.update_result_table_view()
        
        # Assert
        # Check that tables were cleared
        for table in self.view.result_tables:
            table.delete.assert_called()
        
        # Check that first two tables got columns set
        expected_cols1 = list(self.test_df1.columns)
        expected_cols2 = list(self.test_df2.columns)
        
        self.view.result_tables[0].__setitem__.assert_called_with('columns', expected_cols1)
        self.view.result_tables[1].__setitem__.assert_called_with('columns', expected_cols2)
        
        # Check that rows were inserted for non-empty DataFrames
        assert self.view.result_tables[0].insert.call_count == len(self.test_df1)
        assert self.view.result_tables[1].insert.call_count == len(self.test_df2)
    
    def test_update_result_table_view_empty_data(self):
        """Test updating result table view with no data."""
        # Arrange
        self.view._result_dfs = [None, None, None, None]
        
        # Act
        self.view.update_result_table_view()
        
        # Assert
        for table in self.view.result_tables:
            table.delete.assert_called()
            table.__setitem__.assert_called_with('columns', [])
    
    def test_update_result_table_view_initializes_sort_states(self):
        """Test that sort states are initialized properly."""
        # Arrange
        self.view._result_dfs = [self.test_df1.copy()]
        
        # Act
        self.view.update_result_table_view()
        
        # Assert
        assert hasattr(self.view, '_sort_states')
        assert len(self.view._sort_states) == len(self.view.result_tables)
    
    # Tests for _sort_result_column method
    def test_sort_result_column_ascending(self):
        """Test sorting result column in ascending order."""
        # Arrange
        df = self.test_df1.copy()
        self.view._result_dfs = [df, None, None, None]
        mock_tree = Mock()
        mock_tree.delete = Mock()
        mock_tree.get_children = Mock(return_value=[])
        mock_tree.insert = Mock()
        mock_tree.heading = Mock()
        
        # Act
        self.view._sort_result_column(0, mock_tree, 'age', False)
        
        # Assert
        mock_tree.delete.assert_called()
        # Should insert 3 rows (Bob, Alice, Charlie by age)
        assert mock_tree.insert.call_count == 3
        
        # Check sort state was updated
        assert hasattr(self.view, '_sort_states')
        assert self.view._sort_states[0]['age'] == True  # ascending = not reverse
    
    def test_sort_result_column_descending(self):
        """Test sorting result column in descending order."""
        # Arrange
        df = self.test_df1.copy()
        self.view._result_dfs = [df, None, None, None]
        mock_tree = Mock()
        mock_tree.delete = Mock()
        mock_tree.get_children = Mock(return_value=[])
        mock_tree.insert = Mock()
        mock_tree.heading = Mock()
        
        # Act
        self.view._sort_result_column(0, mock_tree, 'age', True)
        
        # Assert
        mock_tree.delete.assert_called()
        assert mock_tree.insert.call_count == 3
        assert self.view._sort_states[0]['age'] == False  # descending = not reverse
    
    def test_sort_result_column_empty_dataframe(self):
        """Test sorting with empty DataFrame."""
        # Arrange
        self.view._result_dfs = [None, None, None, None]
        mock_tree = Mock()
        
        # Act
        self.view._sort_result_column(0, mock_tree, 'age', False)
        
        # Assert - should not crash and not call tree methods
        mock_tree.delete.assert_not_called()
        mock_tree.insert.assert_not_called()
    
    def test_sort_result_column_invalid_column(self):
        """Test sorting with invalid column name."""
        # Arrange
        df = self.test_df1.copy()
        self.view._result_dfs = [df, None, None, None]
        mock_tree = Mock()
        mock_tree.delete = Mock()
        mock_tree.insert = Mock()
        
        # Act
        self.view._sort_result_column(0, mock_tree, 'nonexistent_column', False)
        
        # Assert - should handle exception gracefully
        mock_tree.delete.assert_not_called()
        mock_tree.insert.assert_not_called()
    
    # Tests for sync_column_selection method
    def test_sync_column_selection_matching_column(self):
        """Test syncing column selection when column exists in both DataFrames."""
        # Arrange
        self.view.df1 = self.test_df1.copy()
        self.view.df2 = self.test_df2.copy()
        self.view.column_combo1.get.return_value = 'name'  # Common column
        
        # Act
        self.view.sync_column_selection()
        
        # Assert
        self.view.column_combo2.set.assert_called_once_with('name')
    
    def test_sync_column_selection_non_matching_column(self):
        """Test syncing when selected column doesn't exist in second DataFrame."""
        # Arrange
        self.view.df1 = self.test_df1.copy()
        self.view.df2 = self.test_df2.copy()
        self.view.column_combo1.get.return_value = 'city'  # Only in df1
        
        # Act
        self.view.sync_column_selection()
        
        # Assert
        self.view.column_combo2.set.assert_not_called()
    
    def test_sync_column_selection_no_df2(self):
        """Test syncing when df2 is not loaded."""
        # Arrange
        self.view.df1 = self.test_df1.copy()
        self.view.df2 = None
        self.view.column_combo1.get.return_value = 'name'
        
        # Act
        self.view.sync_column_selection()
        
        # Assert
        self.view.column_combo2.set.assert_not_called()
    
    def test_sync_column_selection_empty_selection(self):
        """Test syncing with empty column selection."""
        # Arrange
        self.view.df1 = self.test_df1.copy()
        self.view.df2 = self.test_df2.copy()
        self.view.column_combo1.get.return_value = ''
        
        # Act
        self.view.sync_column_selection()
        
        # Assert
        self.view.column_combo2.set.assert_not_called()
    
    # Tests for update_filter_buttons method
    def test_update_filter_buttons_both_dataframes_loaded(self):
        """Test filter button states when both DataFrames are loaded."""
        # Arrange
        self.view.df1 = self.test_df1.copy()
        self.view.df2 = self.test_df2.copy()
        
        # Act
        self.view.update_filter_buttons()
        
        # Assert
        self.view.filter1_btn.config.assert_called_once_with(state='normal')
        self.view.filter2_btn.config.assert_called_once_with(state='normal')
    
    def test_update_filter_buttons_only_df1_loaded(self):
        """Test filter button states when only df1 is loaded."""
        # Arrange
        self.view.df1 = self.test_df1.copy()
        self.view.df2 = None
        
        # Act
        self.view.update_filter_buttons()
        
        # Assert
        self.view.filter1_btn.config.assert_called_once_with(state='normal')
        self.view.filter2_btn.config.assert_called_once_with(state='disabled')
    
    def test_update_filter_buttons_only_df2_loaded(self):
        """Test filter button states when only df2 is loaded."""
        # Arrange
        self.view.df1 = None
        self.view.df2 = self.test_df2.copy()
        
        # Act
        self.view.update_filter_buttons()
        
        # Assert
        self.view.filter1_btn.config.assert_called_once_with(state='disabled')
        self.view.filter2_btn.config.assert_called_once_with(state='normal')
    
    def test_update_filter_buttons_no_dataframes(self):
        """Test filter button states when no DataFrames are loaded."""
        # Arrange
        self.view.df1 = None
        self.view.df2 = None
        
        # Act
        self.view.update_filter_buttons()
        
        # Assert
        self.view.filter1_btn.config.assert_called_once_with(state='disabled')
        self.view.filter2_btn.config.assert_called_once_with(state='disabled')
    
    # Tests for open_filter_window method
    @patch('csvlotte.views.filter_view.FilterView')
    def test_open_filter_window_file1_success(self, mock_filter_view):
        """Test opening filter window for file 1."""
        # Arrange
        self.view.df1 = self.test_df1.copy()
        self.view.filter1_var = Mock()
        self.view.file1_path = '/path/to/file1.csv'
        
        # Act
        self.view.open_filter_window(1)
        
        # Assert
        mock_filter_view.assert_called_once()
        call_args = mock_filter_view.call_args
        assert call_args[0][1] is self.view.df1  # DataFrame passed
        assert call_args[0][2] is self.view.filter1_var  # Filter variable passed
        assert call_args[0][3] == 'Filter für CSV 1'  # Title
    
    @patch('csvlotte.views.filter_view.FilterView')
    def test_open_filter_window_file2_success(self, mock_filter_view):
        """Test opening filter window for file 2."""
        # Arrange
        self.view.df2 = self.test_df2.copy()
        self.view.filter2_var = Mock()
        self.view.file2_path = '/path/to/file2.csv'
        
        # Act
        self.view.open_filter_window(2)
        
        # Assert
        mock_filter_view.assert_called_once()
        call_args = mock_filter_view.call_args
        assert call_args[0][1] is self.view.df2
        assert call_args[0][2] is self.view.filter2_var
        assert call_args[0][3] == 'Filter für CSV 2'
    
    @patch('csvlotte.views.home_view.messagebox.showwarning')
    def test_open_filter_window_no_dataframe(self, mock_showwarning):
        """Test opening filter window when no DataFrame is loaded."""
        # Arrange
        self.view.df1 = None
        
        # Act
        self.view.open_filter_window(1)
        
        # Assert
        mock_showwarning.assert_called_once_with('Hinweis', 'Bitte zuerst eine Datei für CSV 1 laden.')
    
    # Integration test for filter callback
    def test_open_filter_window_callback_integration(self):
        """Test that filter window callback integrates correctly with controller."""
        # Arrange
        self.view.df1 = self.test_df1.copy()
        self.view.filter1_var = Mock()
        self.view.file1_path = '/path/to/file1.csv'
        
        # Mock FilterController and its apply_filter method
        with patch('csvlotte.views.filter_view.FilterView') as mock_filter_view:
            # Get the callback function that would be passed to FilterView
            self.view.open_filter_window(1)
            
            # Extract the on_apply callback from the call
            call_kwargs = mock_filter_view.call_args[1]
            on_apply_callback = call_kwargs.get('apply_callback')
            
            assert on_apply_callback is not None
            
            # Test the callback with a mock filtered DataFrame
            with patch('csvlotte.controllers.filter_controller.FilterController') as mock_fc_class:
                mock_fc = Mock()
                mock_fc_class.return_value = mock_fc
                filtered_df = self.test_df1.iloc[:2]  # Simulate filtered result
                mock_fc.apply_filter.return_value = filtered_df
                
                # Call the callback
                on_apply_callback('age > 25')
                
                # Assert controller methods were called
                self.mock_controller.update_columns.assert_called_once()
                self.mock_controller.enable_compare_btn.assert_called_once()
                
                # Assert DataFrame was updated
                assert self.view.df1.equals(filtered_df)
    
    # Edge case tests
    def test_sort_with_nan_values(self):
        """Test sorting columns that contain NaN values."""
        # Arrange
        df_with_nan = pd.DataFrame({
            'name': ['Alice', 'Bob', None],
            'age': [25, None, 35]
        })
        self.view._result_dfs = [df_with_nan, None, None, None]
        mock_tree = Mock()
        mock_tree.delete = Mock()
        mock_tree.get_children = Mock(return_value=[])
        mock_tree.insert = Mock()
        mock_tree.heading = Mock()
        
        # Act
        self.view._sort_result_column(0, mock_tree, 'age', False)
        
        # Assert - should handle NaN values gracefully
        mock_tree.delete.assert_called()
        assert mock_tree.insert.call_count == 3
    
    def test_update_result_table_view_column_width_calculation(self):
        """Test that column widths are calculated correctly."""
        # Arrange
        df_long_text = pd.DataFrame({
            'short': ['A', 'B'],
            'very_long_column_name_that_should_be_truncated': ['Very long text value that exceeds normal width', 'Another long value']
        })
        self.view._result_dfs = [df_long_text, None, None, None]
        
        # Act
        self.view.update_result_table_view()
        
        # Assert - column method should be called with width calculations
        assert self.view.result_tables[0].column.call_count == 2  # Two columns
        
        # Check that width calculations were made (actual values depend on implementation)
        calls = self.view.result_tables[0].column.call_args_list
        for call in calls:
            assert 'width' in call[1]
            assert call[1]['width'] >= 80  # Minimum width
            assert call[1]['width'] <= 300  # Maximum width


if __name__ == "__main__":
    pytest.main([__file__])
