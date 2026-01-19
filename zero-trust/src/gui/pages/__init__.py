"""
Страницы приложения
"""

from .dashboard import DashboardPage
from .scanner import ScannerPage
from .constructor import ConstructorPage
try:
    from .generator import GeneratorPage
except ImportError:
    GeneratorPage = None  # Временное решение
from .validator import ValidatorPage
from .reports import ReportsPage
from .settings import SettingsPage

__all__ = [
    'DashboardPage',
    'ScannerPage',
    'ConstructorPage',
    'GeneratorPage',
    'ValidatorPage',
    'ReportsPage',
    'SettingsPage',
]
