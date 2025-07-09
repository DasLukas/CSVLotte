"""
PyInstaller hook for csvlotte package.
This ensures all csvlotte modules are properly included in the build.
"""

from PyInstaller.utils.hooks import collect_all

# Collect all modules from the csvlotte package
datas, binaries, hiddenimports = collect_all('csvlotte')

# Add additional hidden imports
hiddenimports += [
    'csvlotte',
    'csvlotte.controllers',
    'csvlotte.controllers.home_controller',
    'csvlotte.controllers.filter_controller',
    'csvlotte.controllers.filter_export_controller',
    'csvlotte.controllers.compare_export_controller',
    'csvlotte.views',
    'csvlotte.views.home_view',
    'csvlotte.views.filter_view',
    'csvlotte.views.filter_export_view',
    'csvlotte.views.compare_export_view',
    'csvlotte.views.menubar_settings_view',
    'csvlotte.utils',
    'csvlotte.utils.helpers',
    'csvlotte.utils.translation',
    'csvlotte.utils.embedded_readme',
]
