"""
Translation utility for CSVLotte application.
Provides centralized translation management for multiple languages.
"""

import json
import os
from typing import Dict, Optional


class Translation:
    """
    Central translation manager for the CSVLotte application.
    Loads translations from JSON file and provides access to localized strings.
    """
    
    _instance: Optional['Translation'] = None
    _translations: Dict[str, Dict[str, str]] = {}
    _current_language: str = 'de'
    
    def __new__(cls) -> 'Translation':
        """Singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_translations()
        return cls._instance
    
    def _load_translations(self) -> None:
        """Load translations from JSON file in assets directory."""
        try:
            # Find assets directory relative to this file
            base_dir = os.path.dirname(os.path.dirname(__file__))  # Go up two levels from utils
            assets_dir = os.path.join(base_dir, 'assets')
            translations_path = os.path.join(assets_dir, 'translations.json')
            
            with open(translations_path, 'r', encoding='utf-8') as f:
                self._translations = json.load(f)
        except Exception as e:
            print(f"Fehler beim Laden der Übersetzungen: {e}")
            # Fallback to empty dictionaries
            self._translations = {'de': {}, 'en': {}}
    
    def set_language(self, language: str, save_to_config: bool = True) -> None:
        """
        Set the current language.
        
        Args:
            language: Language code ('de', 'en', etc.)
            save_to_config: Whether to save the language to config file
        """
        if language in self._translations:
            self._current_language = language
            if save_to_config:
                self._save_language_settings()
        else:
            print(f"Warning: Language '{language}' not found, keeping current language")
    
    def get_language(self) -> str:
        """Get the current language code."""
        return self._current_language
    
    def get_text(self, key: str, language: Optional[str] = None) -> str:
        """
        Get translated text for a given key.
        
        Args:
            key: Translation key
            language: Language code (if None, uses current language)
            
        Returns:
            Translated text or the key itself if translation not found
        """
        lang = language or self._current_language
        return self._translations.get(lang, {}).get(key, key)
    
    def get_available_languages(self) -> list:
        """Get list of available language codes."""
        return list(self._translations.keys())
    
    def reload_translations(self) -> None:
        """Reload translations from file (useful for development)."""
        self._load_translations()
    
    def load_language_settings(self) -> None:
        """Load language settings from config file."""
        try:
            import os
            config_dir = os.path.expanduser('~/.csvlotte')
            os.makedirs(config_dir, exist_ok=True)
            config_file = os.path.join(config_dir, 'settings.json')
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    language = settings.get('language', 'de')
                    self.set_language(language, save_to_config=False)  # Don't save when loading
        except Exception:
            self.set_language('de', save_to_config=False)
    
    def _save_language_settings(self) -> None:
        """Save language settings to config file."""
        try:
            import os
            config_dir = os.path.expanduser('~/.csvlotte')
            os.makedirs(config_dir, exist_ok=True)
            config_file = os.path.join(config_dir, 'settings.json')
            
            settings = {'language': self._current_language}
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
        except Exception:
            pass


class TranslationMixin:
    """
    Mixin class that provides translation functionality to any class.
    Use this in views that need translation support.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._translation = Translation()
        # Try to detect language from parent if available
        if hasattr(self, 'master') or hasattr(self, 'parent'):
            parent = getattr(self, 'master', None) or getattr(self, 'parent', None)
            if parent:
                detected_lang = self._detect_language_from_parent(parent)
                if detected_lang:
                    self._translation.set_language(detected_lang)
    
    def _detect_language_from_parent(self, parent) -> Optional[str]:
        """
        Try to detect language from parent widget hierarchy.
        
        Args:
            parent: Parent widget
            
        Returns:
            Language code if found, None otherwise
        """
        try:
            obj = parent
            checked = set()
            while obj is not None and id(obj) not in checked:
                checked.add(id(obj))
                
                # Check for translation object
                if hasattr(obj, '_translation') and hasattr(obj._translation, 'get_language'):
                    return obj._translation.get_language()
                
                # Check for current_language attribute
                if hasattr(obj, 'current_language'):
                    lang = getattr(obj, 'current_language')
                    if lang:
                        return lang
                
                # Move to next parent in hierarchy
                obj = getattr(obj, 'master', None)
        except Exception:
            pass
        return None
    
    def _get_text(self, key: str) -> str:
        """Get translated text for current language."""
        return self._translation.get_text(key)
    
    def _set_language(self, language: str) -> None:
        """Set the translation language."""
        self._translation.set_language(language)
    
    def _load_language_settings(self) -> None:
        """Load language settings from config file."""
        self._translation.load_language_settings()
    
    def _get_current_language(self) -> str:
        """Get current language code."""
        return self._translation.get_language()


# Convenience functions for standalone usage
def get_translation() -> Translation:
    """Get the singleton Translation instance."""
    return Translation()

def get_text(key: str, language: Optional[str] = None) -> str:
    """
    Convenience function to get translated text.
    
    Args:
        key: Translation key
        language: Language code (optional)
        
    Returns:
        Translated text
    """
    return Translation().get_text(key, language)

def set_language(language: str) -> None:
    """
    Convenience function to set the current language.
    
    Args:
        language: Language code
    """
    Translation().set_language(language)
