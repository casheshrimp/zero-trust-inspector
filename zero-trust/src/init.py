"""
ZeroTrust Inspector - Визуализатор и валидатор Zero-Trust политик
"""

__version__ = "1.0.0"
__author__ = "ZeroTrust Project"

# Абсолютные импорты для предотвращения ошибок
from src.core.models import NetworkDevice, SecurityZone, NetworkPolicy
from src.scanner.network_scanner import NetworkScanner
from src.gui.main_window import MainWindow

__all__ = [
    'NetworkDevice',
    'SecurityZone', 
    'NetworkPolicy',
    'NetworkScanner',
    'MainWindow',
]
