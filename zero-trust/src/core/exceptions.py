"""
Пользовательские исключения
"""

class ZeroTrustError(Exception):
    """Базовое исключение для ZeroTrust Inspector"""
    pass

class ScanError(ZeroTrustError):
    """Ошибки сканирования"""
    pass

class DeviceClassificationError(ZeroTrustError):
    """Ошибка классификации устройства"""
    pass

class PolicyValidationError(ZeroTrustError):
    """Ошибка валидации политики"""
    pass

class RuleGenerationError(ZeroTrustError):
    """Ошибка генерации правил"""
    pass

class ConfigurationError(ZeroTrustError):
    """Ошибка конфигурации"""
    pass

class FileSystemError(ZeroTrustError):
    """Ошибка файловой системы"""
    pass

class PermissionError(ZeroTrustError):
    """Ошибка прав доступа"""
    pass

class NetworkError(ZeroTrustError):
    """Сетевая ошибка"""
    pass

class TemplateError(ZeroTrustError):
    """Ошибка шаблона"""
    pass
