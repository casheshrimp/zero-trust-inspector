"""
Константы для ZeroTrust Inspector
"""

# Версия приложения
APP_VERSION = "1.0.0"
APP_NAME = "ZeroTrust Inspector"

# Пути к файлам
CONFIG_DIR = "configs"
EXPORT_DIR = "exports"
BACKUP_DIR = "backups"
LOG_DIR = "logs"
ASSETS_DIR = "assets"

# Настройки сканирования
DEFAULT_NETWORK = "192.168.1.0/24"
SCAN_TIMEOUT = 2
MAX_SCAN_THREADS = 10

# Порты для сканирования
COMMON_PORTS = [22, 23, 80, 443, 8080, 3389, 5353, 9100, 1900, 554]

# Настройки политик по умолчанию
DEFAULT_ZONE_NAMES = {
    "trusted": "Доверенная зона",
    "iot": "IoT устройства",
    "guest": "Гостевая сеть",
    "server": "Серверы",
    "dmz": "DMZ",
}

# Цвета зон
ZONE_COLORS = {
    "trusted": "#4CAF50",  # Зеленый
    "iot": "#FF9800",      # Оранжевый
    "guest": "#9C27B0",    # Фиолетовый
    "server": "#2196F3",   # Синий
    "dmz": "#F44336",      # Красный
    "custom": "#607D8B",   # Серый
}

# Уровни риска
RISK_LEVELS = {
    "low": 0.3,
    "medium": 0.6,
    "high": 0.8,
}
