"""
Tests for the Translation utility module.
"""

import json
import os
import tempfile
import pytest
from unittest.mock import mock_open, patch, MagicMock
from pathlib import Path

# Add src to path to import modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from csvlotte.utils.translation import Translation, TranslationMixin, get_translation, get_text, set_language


class TestTranslation:
    """Test cases for the Translation class."""

    def setup_method(self):
        """Setup for each test method."""
        # Reset the singleton instance
        Translation._instance = None
        Translation._translations = {}
        Translation._current_language = 'de'

    def test_singleton_pattern(self):
        """Test that Translation follows singleton pattern."""
        t1 = Translation()
        t2 = Translation()
        assert t1 is t2

    @patch('builtins.open', new_callable=mock_open, read_data='{"de": {"test": "Test DE"}, "en": {"test": "Test EN"}}')
    def test_load_translations_success(self, mock_file):
        """Test successful loading of translations."""
        translation = Translation()
        assert translation._translations == {"de": {"test": "Test DE"}, "en": {"test": "Test EN"}}
        assert translation._current_language == 'de'

    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    @patch('builtins.print')
    def test_load_translations_file_not_found(self, mock_print, mock_file):
        """Test handling of missing translation file."""
        translation = Translation()
        assert translation._translations == {'de': {}, 'en': {}}
        mock_print.assert_called_once()

    @patch('builtins.open', side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
    @patch('builtins.print')
    def test_load_translations_invalid_json(self, mock_print, mock_file):
        """Test handling of invalid JSON in translation file."""
        translation = Translation()
        assert translation._translations == {'de': {}, 'en': {}}
        mock_print.assert_called_once()

    def test_set_language_valid(self):
        """Test setting a valid language."""
        translation = Translation()
        translation._translations = {"de": {}, "en": {}}
        
        with patch.object(translation, '_save_language_settings') as mock_save:
            translation.set_language('en')
            assert translation._current_language == 'en'
            mock_save.assert_called_once()

    def test_set_language_invalid(self):
        """Test setting an invalid language."""
        translation = Translation()
        translation._translations = {"de": {}, "en": {}}
        
        with patch('builtins.print') as mock_print:
            translation.set_language('fr')
            assert translation._current_language == 'de'  # Should remain unchanged
            mock_print.assert_called_once()

    def test_set_language_no_save(self):
        """Test setting language without saving to config."""
        translation = Translation()
        translation._translations = {"de": {}, "en": {}}
        
        with patch.object(translation, '_save_language_settings') as mock_save:
            translation.set_language('en', save_to_config=False)
            assert translation._current_language == 'en'
            mock_save.assert_not_called()

    def test_get_language(self):
        """Test getting current language."""
        translation = Translation()
        translation._current_language = 'en'
        assert translation.get_language() == 'en'

    def test_get_text_current_language(self):
        """Test getting text for current language."""
        translation = Translation()
        translation._translations = {"de": {"hello": "Hallo"}, "en": {"hello": "Hello"}}
        translation._current_language = 'de'
        
        assert translation.get_text("hello") == "Hallo"

    def test_get_text_specific_language(self):
        """Test getting text for specific language."""
        translation = Translation()
        translation._translations = {"de": {"hello": "Hallo"}, "en": {"hello": "Hello"}}
        translation._current_language = 'de'
        
        assert translation.get_text("hello", "en") == "Hello"

    def test_get_text_key_not_found(self):
        """Test getting text for non-existent key."""
        translation = Translation()
        translation._translations = {"de": {"hello": "Hallo"}, "en": {"hello": "Hello"}}
        translation._current_language = 'de'
        
        assert translation.get_text("nonexistent") == "nonexistent"

    def test_get_text_language_not_found(self):
        """Test getting text for non-existent language."""
        translation = Translation()
        translation._translations = {"de": {"hello": "Hallo"}, "en": {"hello": "Hello"}}
        translation._current_language = 'de'
        
        assert translation.get_text("hello", "fr") == "hello"

    def test_get_available_languages(self):
        """Test getting available languages."""
        translation = Translation()
        translation._translations = {"de": {}, "en": {}, "fr": {}}
        
        languages = translation.get_available_languages()
        assert set(languages) == {"de", "en", "fr"}

    @patch.object(Translation, '_load_translations')
    def test_reload_translations(self, mock_load):
        """Test reloading translations."""
        translation = Translation()
        translation.reload_translations()
        mock_load.assert_called()

    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data='{"language": "en"}')
    def test_load_language_settings_success(self, mock_file, mock_exists):
        """Test successful loading of language settings."""
        translation = Translation()
        translation._translations = {"de": {}, "en": {}}
        
        with patch.object(translation, 'set_language') as mock_set:
            translation.load_language_settings()
            mock_set.assert_called_once_with('en', save_to_config=False)

    @patch('os.path.exists', return_value=False)
    def test_load_language_settings_no_file(self, mock_exists):
        """Test loading language settings when config file doesn't exist."""
        translation = Translation()
        translation._translations = {"de": {}, "en": {}}
        
        with patch.object(translation, 'set_language') as mock_set:
            translation.load_language_settings()
            mock_set.assert_not_called()

    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
    def test_load_language_settings_invalid_json(self, mock_file, mock_exists):
        """Test handling of invalid JSON in config file."""
        translation = Translation()
        translation._translations = {"de": {}, "en": {}}
        
        with patch.object(translation, 'set_language') as mock_set:
            translation.load_language_settings()
            mock_set.assert_called_once_with('de', save_to_config=False)

    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch.object(Translation, '_load_translations')
    def test_save_language_settings_success(self, mock_load, mock_file, mock_makedirs):
        """Test successful saving of language settings."""
        translation = Translation()
        translation._current_language = 'en'
        
        translation._save_language_settings()
        
        mock_makedirs.assert_called_once()
        # Check that open was called for writing the settings file
        mock_file.assert_called_with(
            os.path.join(os.path.expanduser('~/.csvlotte'), 'settings.json'),
            'w',
            encoding='utf-8'
        )
        handle = mock_file()
        handle.write.assert_called()

    @patch('os.makedirs', side_effect=OSError("Permission denied"))
    def test_save_language_settings_failure(self, mock_makedirs):
        """Test handling of failure when saving language settings."""
        translation = Translation()
        translation._current_language = 'en'
        
        # Should not raise exception
        translation._save_language_settings()


class TestTranslationMixin:
    """Test cases for the TranslationMixin class."""

    def setup_method(self):
        """Setup for each test method."""
        # Reset the singleton instance
        Translation._instance = None
        Translation._translations = {}
        Translation._current_language = 'de'

    def test_mixin_initialization(self):
        """Test TranslationMixin initialization."""
        class TestClass(TranslationMixin):
            pass
        
        with patch.object(Translation, '_load_translations'):
            obj = TestClass()
            assert hasattr(obj, '_translation')
            assert isinstance(obj._translation, Translation)

    def test_mixin_with_master_parent(self):
        """Test TranslationMixin with master parent."""
        class TestClass(TranslationMixin):
            def __init__(self):
                self.master = MagicMock()
                super().__init__()
        
        # Create a mock parent with translation object
        parent = MagicMock()
        parent._translation = MagicMock()
        parent._translation.get_language.return_value = 'en'
        
        with patch.object(Translation, '_load_translations'):
            obj = TestClass()
            obj.master = parent
            
            # Test the actual language detection method
            result = obj._detect_language_from_parent(parent)
            assert result == 'en'

    def test_mixin_with_parent_attribute(self):
        """Test TranslationMixin with parent attribute."""
        class TestClass(TranslationMixin):
            def __init__(self):
                self.parent = MagicMock()
                super().__init__()
        
        # Create a mock parent with current_language attribute but no _translation
        parent = MagicMock()
        parent.current_language = 'en'
        # Explicitly remove _translation attribute to ensure we test current_language path
        del parent._translation
        
        with patch.object(Translation, '_load_translations'):
            obj = TestClass()
            obj.parent = parent
            
            # Test the actual language detection method
            result = obj._detect_language_from_parent(parent)
            assert result == 'en'

    def test_mixin_with_parent_no_language_detected(self):
        """Test TranslationMixin with parent but no language detected."""
        class TestClass(TranslationMixin):
            def __init__(self):
                self.parent = MagicMock()
                super().__init__()
        
        with patch.object(Translation, '_load_translations'):
            with patch.object(TranslationMixin, '_detect_language_from_parent', return_value=None) as mock_detect:
                with patch.object(Translation, 'set_language') as mock_set_lang:
                    obj = TestClass()
                    mock_detect.assert_called_once()
                    mock_set_lang.assert_not_called()

    def test_mixin_language_setting_integration(self):
        """Test that TranslationMixin actually sets language when parent has language."""
        class TestClass(TranslationMixin):
            def __init__(self):
                self.master = MagicMock()
                self.master._translation = MagicMock()
                self.master._translation.get_language.return_value = 'en'
                super().__init__()
        
        with patch.object(Translation, '_load_translations'):
            # Create translation instance with available languages
            with patch.object(Translation, '_translations', {"de": {}, "en": {}}):
                with patch.object(Translation, 'set_language') as mock_set_lang:
                    obj = TestClass()
                    # Should detect 'en' from parent and set it
                    mock_set_lang.assert_called_once_with('en')

    def test_detect_language_from_parent_with_translation(self):
        """Test language detection from parent with translation object."""
        class TestClass(TranslationMixin):
            pass
        
        parent = MagicMock()
        parent._translation = MagicMock()
        parent._translation.get_language.return_value = 'en'
        
        with patch.object(Translation, '_load_translations'):
            obj = TestClass()
            result = obj._detect_language_from_parent(parent)
            assert result == 'en'

    def test_detect_language_from_parent_with_current_language(self):
        """Test language detection from parent with current_language attribute."""
        class TestClass(TranslationMixin):
            pass
        
        parent = MagicMock()
        parent.current_language = 'en'
        # Explicitly remove _translation attribute to ensure we test current_language path
        del parent._translation
        
        with patch.object(Translation, '_load_translations'):
            obj = TestClass()
            result = obj._detect_language_from_parent(parent)
            assert result == 'en'

    def test_detect_language_from_parent_none(self):
        """Test language detection with None parent."""
        class TestClass(TranslationMixin):
            pass
        
        with patch.object(Translation, '_load_translations'):
            obj = TestClass()
            result = obj._detect_language_from_parent(None)
            assert result is None

    def test_detect_language_from_parent_no_attributes(self):
        """Test language detection from parent without relevant attributes."""
        class TestClass(TranslationMixin):
            pass
        
        parent = MagicMock()
        del parent._translation
        del parent.current_language
        parent.master = None
        
        with patch.object(Translation, '_load_translations'):
            obj = TestClass()
            result = obj._detect_language_from_parent(parent)
            assert result is None

    def test_mixin_get_text(self):
        """Test _get_text method in mixin."""
        class TestClass(TranslationMixin):
            pass
        
        with patch.object(Translation, '_load_translations'):
            obj = TestClass()
            obj._translation._translations = {"de": {"hello": "Hallo"}}
            obj._translation._current_language = 'de'
            
            assert obj._get_text("hello") == "Hallo"

    def test_mixin_set_language(self):
        """Test _set_language method in mixin."""
        class TestClass(TranslationMixin):
            pass
        
        with patch.object(Translation, '_load_translations'):
            obj = TestClass()
            obj._translation._translations = {"de": {}, "en": {}}
            
            with patch.object(obj._translation, '_save_language_settings'):
                obj._set_language('en')
                assert obj._translation._current_language == 'en'

    def test_mixin_load_language_settings(self):
        """Test _load_language_settings method in mixin."""
        class TestClass(TranslationMixin):
            pass
        
        with patch.object(Translation, '_load_translations'):
            obj = TestClass()
            
            with patch.object(obj._translation, 'load_language_settings') as mock_load:
                obj._load_language_settings()
                mock_load.assert_called_once()

    def test_mixin_get_current_language(self):
        """Test _get_current_language method in mixin."""
        class TestClass(TranslationMixin):
            pass
        
        with patch.object(Translation, '_load_translations'):
            obj = TestClass()
            obj._translation._current_language = 'en'
            
            assert obj._get_current_language() == 'en'


class TestConvenienceFunctions:
    """Test cases for convenience functions."""

    def setup_method(self):
        """Setup for each test method."""
        # Reset the singleton instance
        Translation._instance = None
        Translation._translations = {}
        Translation._current_language = 'de'

    def test_get_translation(self):
        """Test get_translation convenience function."""
        with patch.object(Translation, '_load_translations'):
            translation = get_translation()
            assert isinstance(translation, Translation)

    def test_get_text_convenience(self):
        """Test get_text convenience function."""
        with patch.object(Translation, '_load_translations'):
            with patch.object(Translation, 'get_text', return_value='Test') as mock_get:
                result = get_text('test_key', 'en')
                assert result == 'Test'
                mock_get.assert_called_once_with('test_key', 'en')

    def test_set_language_convenience(self):
        """Test set_language convenience function."""
        with patch.object(Translation, '_load_translations'):
            with patch.object(Translation, 'set_language') as mock_set:
                set_language('en')
                mock_set.assert_called_once_with('en')


class TestIntegration:
    """Integration tests with real translation data."""

    def setup_method(self):
        """Setup for each test method."""
        # Reset the singleton instance
        Translation._instance = None
        Translation._translations = {}
        Translation._current_language = 'de'

    def test_with_real_translation_data(self):
        """Test with actual translation data structure."""
        test_translations = {
            "de": {
                "title": "CSVLotte - CSV Vergleichstool",
                "hello": "Hallo",
                "settings": "Einstellungen"
            },
            "en": {
                "title": "CSVLotte - CSV Comparison Tool",
                "hello": "Hello",
                "settings": "Settings"
            }
        }
        
        with patch('builtins.open', new_callable=mock_open, read_data=json.dumps(test_translations)):
            translation = Translation()
            
            # Test German translations
            assert translation.get_text("title") == "CSVLotte - CSV Vergleichstool"
            assert translation.get_text("hello") == "Hallo"
            
            # Test English translations
            translation.set_language('en', save_to_config=False)
            assert translation.get_text("title") == "CSVLotte - CSV Comparison Tool"
            assert translation.get_text("hello") == "Hello"
            
            # Test fallback for missing key
            assert translation.get_text("nonexistent") == "nonexistent"

    def test_file_path_resolution(self):
        """Test that file paths are resolved correctly."""
        with patch('os.path.join') as mock_join:
            with patch('builtins.open', new_callable=mock_open, read_data='{"de": {}, "en": {}}'):
                Translation()
                
                # Verify the path construction
                assert mock_join.call_count >= 2  # At least assets_dir and translations_path calls

    def test_config_directory_creation(self):
        """Test that config directory is created properly."""
        translation = Translation()
        translation._translations = {"de": {}, "en": {}}
        
        with patch('os.makedirs') as mock_makedirs:
            with patch('os.path.expanduser', return_value='/home/user/.csvlotte'):
                with patch('builtins.open', new_callable=mock_open):
                    translation._save_language_settings()
                    
                    mock_makedirs.assert_called_once_with('/home/user/.csvlotte', exist_ok=True)


if __name__ == '__main__':
    pytest.main([__file__])