"""
Tests for HomeController class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import pandas as pd
from csvlotte.controllers.home_controller import HomeController



class TestHomeController:
    """Test cases for HomeController."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        # Mock root window
        self.mock_root = Mock()
        
        # Mock the HomeView completely to avoid Tkinter initialization
        self.view_patcher = patch('csvlotte.controllers.home_controller.HomeView')
        self.mock_view_class = self.view_patcher.start()
        self.mock_view = Mock()
        self.mock_view_class.return_value = self.mock_view
        
        # Import and create controller after patching
        self.controller = HomeController(self.mock_root)
        
        # Setup mock view attributes
        self._setup_mock_view_attributes()
        
        # Create test DataFrame
        self.test_df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35],
            'city': ['Berlin', 'Munich', 'Hamburg']
        })
    
    def teardown_method(self):
        """Clean up after each test."""
        self.view_patcher.stop()
    
    def _setup_mock_view_attributes(self):
        """Setup all mock view attributes."""
        # File attributes
        self.mock_view.file1_path = None
        self.mock_view.file2_path = None
        self.mock_view.df1 = None
        self.mock_view.df2 = None
        
        # UI components
        self.mock_view.file1_label = Mock()
        self.mock_view.file2_label = Mock()
        self.mock_view.file1_info_btn = Mock()
        self.mock_view.file2_info_btn = Mock()
        self.mock_view.file1_reload_btn = Mock()
        self.mock_view.file2_reload_btn = Mock()
        self.mock_view.compare_btn = Mock()
        self.mock_view.export_btn = Mock()
        self.mock_view.progress = Mock()
        self.mock_view.notebook = Mock()
        
        # ComboBox mocks with __setitem__ support
        self.mock_view.column_combo1 = MagicMock()
        self.mock_view.column_combo2 = MagicMock()
        
        # Progress bar mock with __setitem__ support
        self.mock_view.progress = MagicMock()
        
        # Variables
        self.mock_view.delim_var1 = Mock()
        self.mock_view.delim_var2 = Mock()
        self.mock_view.encoding_var1 = Mock()
        self.mock_view.encoding_var2 = Mock()
        self.mock_view.filter1_var = Mock()
        self.mock_view.filter2_var = Mock()
        self.mock_view.col1_text_var = Mock()
        self.mock_view.col2_text_var = Mock()
        
        # Methods
        self.mock_view.update_filter_buttons = Mock()
        self.mock_view.open_filter_window = Mock()
        self.mock_view.update_result_table_view = Mock()
        self.mock_view.sync_column_selection = Mock()
        
        # Setup default returns for variables
        self.mock_view.delim_var1.get.return_value = ''
        self.mock_view.delim_var2.get.return_value = ''
        self.mock_view.encoding_var1.get.return_value = ''
        self.mock_view.encoding_var2.get.return_value = ''
        self.mock_view.filter1_var.get.return_value = ''
        self.mock_view.filter2_var.get.return_value = ''
        self.mock_view.col1_text_var.get.return_value = ''
        self.mock_view.col2_text_var.get.return_value = ''
        
        # Additional attributes
        self.mock_view.result_table_labels = ['Label1', 'Label2', 'Label3', 'Label4']
        self.mock_view._result_dfs = []
        self.mock_view.root = self.mock_root

    # Tests for load_file method
    @patch('csvlotte.controllers.home_controller.filedialog.askopenfilename')
    @patch('csvlotte.controllers.home_controller.pd.read_csv')
    def test_load_file1_successful(self, mock_read_csv, mock_filedialog):
        """Test successful loading of file1 with default settings."""
        # Arrange
        test_path = '/path/to/test1.csv'
        mock_filedialog.return_value = test_path
        mock_read_csv.return_value = self.test_df.copy()
        
        # Act
        self.controller.load_file(1)
        
        # Assert
        mock_filedialog.assert_called_once_with(filetypes=[('CSV files', '*.csv')])
        mock_read_csv.assert_called_once_with(test_path, sep=';', encoding='latin1')
        assert self.mock_view.file1_path == test_path
        self.mock_view.file1_label.config.assert_called_once_with(text=test_path)
        self.mock_view.file1_info_btn.config.assert_called_once_with(state='normal')
        self.mock_view.file1_reload_btn.config.assert_called_once_with(state='normal')
        assert self.mock_view.df1.equals(self.test_df)

    @patch('csvlotte.controllers.home_controller.filedialog.askopenfilename')
    def test_load_file_no_path_selected(self, mock_filedialog):
        """Test behavior when user cancels file dialog."""
        # Arrange
        mock_filedialog.return_value = ''
        
        # Act
        self.controller.load_file(1)
        
        # Assert
        mock_filedialog.assert_called_once_with(filetypes=[('CSV files', '*.csv')])
        # Should return early without processing
        assert self.mock_view.df1 is None

    @patch('csvlotte.controllers.home_controller.filedialog.askopenfilename')
    @patch('csvlotte.controllers.home_controller.pd.read_csv')
    @patch('csvlotte.controllers.home_controller.messagebox.showerror')
    def test_load_file_csv_read_error(self, mock_messagebox, mock_read_csv, mock_filedialog):
        """Test handling of CSV reading errors."""
        # Arrange
        test_path = '/path/to/invalid.csv'
        mock_filedialog.return_value = test_path
        mock_read_csv.side_effect = Exception('File format error')
        
        # Act
        self.controller.load_file(1)
        
        # Assert
        mock_messagebox.assert_called_once_with('Fehler', 'Datei 1 konnte nicht geladen werden:\nFile format error')
        assert self.mock_view.df1 is None

    @patch('csvlotte.controllers.home_controller.filedialog.askopenfilename')
    @patch('csvlotte.controllers.home_controller.pd.read_csv')
    def test_load_file_with_custom_delimiter_and_encoding(self, mock_read_csv, mock_filedialog):
        """Test loading file with custom delimiter and encoding."""
        # Arrange
        test_path = '/path/to/test.csv'
        mock_filedialog.return_value = test_path
        mock_read_csv.return_value = self.test_df.copy()
        self.mock_view.delim_var1.get.return_value = ','
        self.mock_view.encoding_var1.get.return_value = 'utf-8'
        
        # Act
        self.controller.load_file(1)
        
        # Assert
        mock_read_csv.assert_called_once_with(test_path, sep=',', encoding='utf-8')

    @patch('csvlotte.controllers.home_controller.filedialog.askopenfilename')
    @patch('csvlotte.controllers.home_controller.pd.read_csv')
    def test_load_file_with_valid_filter(self, mock_read_csv, mock_filedialog):
        """Test loading file with a valid filter applied."""
        # Arrange
        test_path = '/path/to/test.csv'
        mock_filedialog.return_value = test_path
        mock_read_csv.return_value = self.test_df.copy()
        self.mock_view.filter1_var.get.return_value = 'age > 25'
        
        # Act
        self.controller.load_file(1)
        
        # Assert
        # Check that DataFrame was filtered correctly
        assert len(self.mock_view.df1) == 2  # Bob and Charlie (age > 25)

    @patch('csvlotte.controllers.home_controller.filedialog.askopenfilename')
    @patch('csvlotte.controllers.home_controller.pd.read_csv')
    @patch('csvlotte.controllers.home_controller.messagebox.showerror')
    def test_load_file_with_invalid_filter(self, mock_messagebox, mock_read_csv, mock_filedialog):
        """Test handling of invalid filter expressions."""
        # Arrange
        test_path = '/path/to/test.csv'
        mock_filedialog.return_value = test_path
        mock_read_csv.return_value = self.test_df.copy()
        self.mock_view.filter1_var.get.return_value = 'invalid_column > 25'
        
        # Act
        self.controller.load_file(1)
        
        # Assert
        mock_messagebox.assert_called()
        args = mock_messagebox.call_args[0]
        assert args[0] == 'Fehler'
        assert 'Filter für Datei 1 ungültig:' in args[1]

    # Tests for reload_file method
    @patch('csvlotte.controllers.home_controller.pd.read_csv')
    @patch('csvlotte.controllers.home_controller.messagebox.showerror')
    def test_reload_file1_successful(self, mock_messagebox, mock_read_csv):
        """Test successful reload of file1."""
        # Arrange
        test_path = '/path/to/test1.csv'
        self.mock_view.file1_path = test_path
        mock_read_csv.return_value = self.test_df.copy()
        
        # Act
        self.controller.reload_file(1)
        
        # Assert
        mock_read_csv.assert_called_once_with(test_path, sep=';', encoding='latin1')
        assert self.mock_view.df1.equals(self.test_df)
        # Ensure no error message was shown
        mock_messagebox.assert_not_called()

    @patch('csvlotte.controllers.home_controller.pd.read_csv')
    @patch('csvlotte.controllers.home_controller.messagebox.showerror')
    def test_reload_file_csv_error(self, mock_messagebox, mock_read_csv):
        """Test reload file with CSV error."""
        # Arrange
        test_path = '/path/to/test1.csv'
        self.mock_view.file1_path = test_path
        mock_read_csv.side_effect = Exception('Read error')
        
        # Act
        self.controller.reload_file(1)
        
        # Assert
        mock_messagebox.assert_called_once()
        assert self.mock_view.df1 is None

    def test_reload_file_no_path(self):
        """Test reload file when no path is set."""
        # Arrange
        self.mock_view.file1_path = None
        
        # Act
        self.controller.reload_file(1)
        
        # Assert - should not crash, method should complete normally
        # The update methods are called at the end of reload_file regardless of path
        assert True  # Test passes if no exception is raised

    # Tests for show_file_info method
    @patch('os.path.getsize')
    @patch('csvlotte.controllers.home_controller.messagebox.showinfo')
    def test_show_file_info_successful(self, mock_showinfo, mock_getsize):
        """Test showing file info successfully."""
        # Arrange
        test_path = '/path/to/test1.csv'
        self.mock_view.file1_path = test_path
        self.mock_view.df1 = self.test_df.copy()
        mock_getsize.return_value = 2048  # 2KB
        
        # Act
        self.controller.show_file_info(1)
        
        # Assert
        mock_showinfo.assert_called_once()
        args = mock_showinfo.call_args[0]
        assert args[0] == 'Info Datei 1'
        assert test_path in args[1]
        assert '2.0 kB' in args[1]
        assert 'Zeilen: 3' in args[1]
        assert 'Spalten: 3' in args[1]

    @patch('os.path.getsize')
    @patch('csvlotte.controllers.home_controller.messagebox.showinfo')
    def test_show_file_info_file_size_error(self, mock_showinfo, mock_getsize):
        """Test showing file info when file size cannot be determined."""
        # Arrange
        test_path = '/path/to/test1.csv'
        self.mock_view.file1_path = test_path
        self.mock_view.df1 = self.test_df.copy()
        mock_getsize.side_effect = Exception('File not found')
        
        # Act
        self.controller.show_file_info(1)
        
        # Assert
        mock_showinfo.assert_called_once()
        args = mock_showinfo.call_args[0]
        assert '0.0 kB' in args[1]  # Should show 0.0 kB when size cannot be determined

    def test_show_file_info_no_file(self):
        """Test showing file info when no file is loaded."""
        # Arrange
        self.mock_view.file1_path = None
        self.mock_view.df1 = None
        
        # Act
        self.controller.show_file_info(1)
        
        # Assert - should not show any dialog
        with patch('csvlotte.controllers.home_controller.messagebox.showinfo') as mock_showinfo:
            self.controller.show_file_info(1)
            mock_showinfo.assert_not_called()

    # Tests for open_filter_window method
    def test_open_filter_window_file1(self):
        """Test opening filter window for file1."""
        # Act
        self.controller.open_filter_window(1)
        
        # Assert
        self.mock_view.open_filter_window.assert_called_once_with(1)

    def test_open_filter_window_file2(self):
        """Test opening filter window for file2."""
        # Act
        self.controller.open_filter_window(2)
        
        # Assert
        self.mock_view.open_filter_window.assert_called_once_with(2)

    # Tests for compare_csvs method
    @patch('csvlotte.controllers.home_controller.messagebox.showerror')
    def test_compare_csvs_no_columns_selected(self, mock_showerror):
        """Test compare CSVs when no columns are selected."""
        # Arrange
        self.mock_view.column_combo1.get.return_value = ''
        self.mock_view.column_combo2.get.return_value = ''
        
        # Act
        self.controller.compare_csvs()
        
        # Assert
        mock_showerror.assert_called_once_with('Fehler', 'Bitte Vergleichsspalten auswählen!')

    @patch('csvlotte.controllers.home_controller.messagebox.showerror')
    def test_compare_csvs_no_dataframes_loaded(self, mock_showerror):
        """Test compare CSVs when no DataFrames are loaded."""
        # Arrange
        self.mock_view.column_combo1.get.return_value = 'name'
        self.mock_view.column_combo2.get.return_value = 'name'
        self.mock_view.df1 = None
        self.mock_view.df2 = None
        
        # Act
        self.controller.compare_csvs()
        
        # Assert
        mock_showerror.assert_called_once_with('Fehler', 'Bitte beide CSV-Dateien laden!')

    @patch('csvlotte.controllers.home_controller.ttk.Style')
    def test_compare_csvs_successful(self, mock_style):
        """Test successful CSV comparison."""
        # Arrange
        df1 = pd.DataFrame({'name': ['Alice', 'Bob', 'Charlie']})
        df2 = pd.DataFrame({'name': ['Bob', 'David', 'Eve']})
        
        self.mock_view.df1 = df1
        self.mock_view.df2 = df2
        self.mock_view.column_combo1.get.return_value = 'name'
        self.mock_view.column_combo2.get.return_value = 'name'
        self.mock_view.notebook.select.return_value = 'tab1'
        self.mock_view.notebook.index.return_value = 0
        
        # Act
        self.controller.compare_csvs()
        
        # Assert
        assert len(self.mock_view._result_dfs) == 4
        self.mock_view.export_btn.config.assert_called_with(state='normal')
        self.mock_view.update_result_table_view.assert_called_once()

    # Tests for export_results_button method
    @patch('csvlotte.controllers.compare_export_controller.CompareExportController')
    def test_export_results_button(self, mock_export_controller):
        """Test export results button functionality."""
        # Arrange
        self.mock_view.notebook.select.return_value = 'tab1'
        self.mock_view.notebook.index.return_value = 1
        self.mock_view._result_dfs = [Mock(), Mock(), Mock(), Mock()]
        self.mock_view.file1_path = '/path/to/file1.csv'
        mock_controller_instance = Mock()
        mock_export_controller.return_value = mock_controller_instance
        
        # Act
        self.controller.export_results_button()
        
        # Assert
        mock_export_controller.assert_called_once()
        mock_controller_instance.open_export_dialog.assert_called_once()

    @patch('csvlotte.controllers.compare_export_controller.CompareExportController')
    def test_export_results_button_no_file1_path(self, mock_export_controller):
        """Test export results when file1_path is not set."""
        # Arrange
        self.mock_view.notebook.select.return_value = 'tab1'
        self.mock_view.notebook.index.return_value = 1
        self.mock_view._result_dfs = [Mock(), Mock(), Mock(), Mock()]
        delattr(self.mock_view, 'file1_path')  # Remove file1_path attribute
        mock_controller_instance = Mock()
        mock_export_controller.return_value = mock_controller_instance
        
        # Act
        self.controller.export_results_button()
        
        # Assert
        mock_export_controller.assert_called_once()
        # Should be called with default_dir=None
        call_args = mock_export_controller.call_args[0]
        assert call_args[4] is None  # default_dir should be None

    # Tests for update_columns method
    def test_update_columns_both_dataframes(self):
        """Test updating columns when both DataFrames are loaded."""
        # Arrange
        self.mock_view.df1 = self.test_df.copy()
        self.mock_view.df2 = self.test_df.copy()
        
        # Act
        self.controller.update_columns()
        
        # Assert
        expected_columns = list(self.test_df.columns)
        self.mock_view.column_combo1.__setitem__.assert_called_with('values', expected_columns)
        self.mock_view.column_combo2.__setitem__.assert_called_with('values', expected_columns)
        self.mock_view.export_btn.config.assert_called_with(state='disabled')

    def test_update_columns_no_dataframes(self):
        """Test updating columns when no DataFrames are loaded."""
        # Arrange
        self.mock_view.df1 = None
        self.mock_view.df2 = None
        
        # Act
        self.controller.update_columns()
        
        # Assert
        self.mock_view.export_btn.config.assert_called_with(state='disabled')

    def test_update_columns_no_export_btn(self):
        """Test updating columns when export button doesn't exist."""
        # Arrange
        self.mock_view.df1 = self.test_df.copy()
        delattr(self.mock_view, 'export_btn')
        
        # Act & Assert - should not raise an exception
        self.controller.update_columns()

    # Tests for enable_compare_btn method
    def test_enable_compare_btn_both_dataframes_loaded(self):
        """Test enabling compare button when both DataFrames are loaded."""
        # Arrange
        self.mock_view.df1 = self.test_df.copy()
        self.mock_view.df2 = self.test_df.copy()
        
        # Act
        self.controller.enable_compare_btn()
        
        # Assert
        self.mock_view.compare_btn.config.assert_called_once_with(state='normal')

    def test_enable_compare_btn_only_one_dataframe(self):
        """Test disabling compare button when only one DataFrame is loaded."""
        # Arrange
        self.mock_view.df1 = self.test_df.copy()
        self.mock_view.df2 = None
        
        # Act
        self.controller.enable_compare_btn()
        
        # Assert
        self.mock_view.compare_btn.config.assert_called_once_with(state='disabled')

    def test_enable_compare_btn_no_dataframes(self):
        """Test disabling compare button when no DataFrames are loaded."""
        # Arrange
        self.mock_view.df1 = None
        self.mock_view.df2 = None
        
        # Act
        self.controller.enable_compare_btn()
        
        # Assert
        self.mock_view.compare_btn.config.assert_called_once_with(state='disabled')

    # Tests for update_tab_labels method
    def test_update_tab_labels_with_file_paths(self):
        """Test updating tab labels when file paths are set."""
        # Arrange
        self.mock_view.file1_path = '/path/to/file1.csv'
        self.mock_view.file2_path = '/path/to/file2.csv'
        
        # Act
        self.controller.update_tab_labels()
        
        # Assert
        expected_calls = [
            call(0, text='Nur in file1.csv'),
            call(1, text='Gemeinsame file1.csv'),
            call(2, text='Gemeinsame in file2.csv'),
            call(3, text='Nur in file2.csv')
        ]
        self.mock_view.notebook.tab.assert_has_calls(expected_calls)
        self.mock_view.column_combo1.bind.assert_called_once_with(
            '<<ComboboxSelected>>', 
            self.mock_view.sync_column_selection
        )

    def test_update_tab_labels_no_file_paths(self):
        """Test updating tab labels when no file paths are set."""
        # Arrange
        self.mock_view.file1_path = None
        self.mock_view.file2_path = None
        
        # Act
        self.controller.update_tab_labels()
        
        # Assert
        expected_calls = [
            call(0, text='Nur in CSV 1'),
            call(1, text='Gemeinsame CSV 1'),
            call(2, text='Gemeinsame in CSV 2'),
            call(3, text='Nur in CSV 2')
        ]
        self.mock_view.notebook.tab.assert_has_calls(expected_calls)

    def test_update_tab_labels_windows_path_separator(self):
        """Test updating tab labels with Windows path separators."""
        # Arrange
        self.mock_view.file1_path = 'C:\\path\\to\\file1.csv'
        self.mock_view.file2_path = 'C:\\path\\to\\file2.csv'
        
        # Act
        self.controller.update_tab_labels()
        
        # Assert - Should still work with Windows paths
        # Note: The current implementation uses '/' separator, 
        # so this test documents the current behavior
        expected_calls = [
            call(0, text='Nur in C:\\path\\to\\file1.csv'),
            call(1, text='Gemeinsame C:\\path\\to\\file1.csv'),
            call(2, text='Gemeinsame in C:\\path\\to\\file2.csv'),
            call(3, text='Nur in C:\\path\\to\\file2.csv')
        ]
        self.mock_view.notebook.tab.assert_has_calls(expected_calls)


if __name__ == "__main__":
    pytest.main([__file__])