"""
Менеджер для работы с конфигурационными файлами
"""

import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import hashlib

from ..core.constants import CONFIGS_DIR, BACKUPS_DIR
from ..core.exceptions import ConfigurationError

class ConfigManager:
    """Менеджер для работы с конфигурациями приложения"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or CONFIGS_DIR
        self.config_dir.mkdir(exist_ok=True)
        
        self.backup_dir = BACKUPS_DIR
        self.backup_dir.mkdir(exist_ok=True)
        
        self.default_config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Получить конфигурацию по умолчанию"""
        return {
            'application': {
                'name': 'ZeroTrust Inspector',
                'version': '1.0.0',
                'auto_save': True,
                'auto_backup': True,
                'theme': 'dark',
                'language': 'ru',
            },
            'scanning': {
                'network_range': 'auto',
                'scan_speed': 'normal',
                'port_timeout': 1000,
                'max_hosts': 254,
                'auto_classify': True,
            },
            'security': {
                'default_policy': 'deny',
                'auto_isolate_high_risk': True,
                'enable_logging': True,
                'log_retention_days': 30,
            },
            'export': {
                'default_format': 'openwrt',
                'include_backup': True,
                'add_comments': True,
                'timestamp_format': '%Y-%m-%d_%H-%M-%S',
            },
        }
    
    def load_config(self, config_name: str = 'settings') -> Dict[str, Any]:
        """Загрузить конфигурацию из файла"""
        config_path = self.config_dir / f"{config_name}.json"
        
        if not config_path.exists():
            # Если файла нет, создаем с настройками по умолчанию
            return self.create_default_config(config_name)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Объединяем с настройками по умолчанию (для новых полей)
            merged_config = self._merge_configs(self.default_config, config)
            
            return merged_config
            
        except (json.JSONDecodeError, IOError) as e:
            raise ConfigurationError(f"Ошибка загрузки конфигурации: {e}")
    
    def save_config(self, config: Dict[str, Any], config_name: str = 'settings'):
        """Сохранить конфигурацию в файл"""
        config_path = self.config_dir / f"{config_name}.json"
        
        # Создаем backup перед сохранением
        if config_path.exists():
            self.create_backup(config_path)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
        except IOError as e:
            raise ConfigurationError(f"Ошибка сохранения конфигурации: {e}")
    
    def create_default_config(self, config_name: str) -> Dict[str, Any]:
        """Создать конфигурацию по умолчанию"""
        config = self.default_config.copy()
        self.save_config(config, config_name)
        return config
    
    def create_backup(self, filepath: Path):
        """Создать backup файла"""
        if not filepath.exists():
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{filepath.stem}_{timestamp}{filepath.suffix}"
        backup_path = self.backup_dir / backup_name
        
        try:
            import shutil
            shutil.copy2(filepath, backup_path)
            
            # Ограничиваем количество backup файлов
            self._cleanup_old_backups(filepath.stem)
            
        except Exception as e:
            print(f"Ошибка создания backup: {e}")
    
    def _cleanup_old_backups(self, prefix: str, max_backups: int = 10):
        """Удалить старые backup файлы"""
        backup_files = list(self.backup_dir.glob(f"{prefix}_*.json"))
        
        if len(backup_files) > max_backups:
            # Сортируем по времени создания (самые старые первые)
            backup_files.sort(key=lambda x: x.stat().st_mtime)
            
            # Удаляем лишние файлы
            for filepath in backup_files[:-max_backups]:
                try:
                    filepath.unlink()
                except Exception:
                    pass
    
    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """Рекурсивно объединить конфигурации"""
        merged = default.copy()
        
        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def export_config(self, config: Dict, format: str = 'json') -> str:
        """Экспортировать конфигурацию в указанном формате"""
        if format == 'json':
            return json.dumps(config, indent=2, ensure_ascii=False)
        elif format == 'yaml':
            return yaml.dump(config, default_flow_style=False, allow_unicode=True)
        else:
            raise ConfigurationError(f"Неподдерживаемый формат: {format}")
    
    def import_config(self, config_str: str, format: str = 'json') -> Dict:
        """Импортировать конфигурацию из строки"""
        try:
            if format == 'json':
                return json.loads(config_str)
            elif format == 'yaml':
                return yaml.safe_load(config_str)
            else:
                raise ConfigurationError(f"Неподдерживаемый формат: {format}")
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ConfigurationError(f"Ошибка парсинга конфигурации: {e}")
    
    def validate_config(self, config: Dict) -> List[str]:
        """Валидация конфигурации"""
        errors = []
        
        # Проверка обязательных полей
        required_fields = ['application', 'scanning', 'security']
        for field in required_fields:
            if field not in config:
                errors.append(f"Отсутствует обязательный раздел: {field}")
        
        # Проверка значений
        if 'scanning' in config:
            scanning = config['scanning']
            if 'scan_speed' in scanning and scanning['scan_speed'] not in ['slow', 'normal', 'fast']:
                errors.append("Некорректное значение scan_speed. Допустимо: slow, normal, fast")
        
        return errors
    
    def get_config_hash(self, config: Dict) -> str:
        """Получить хэш конфигурации для сравнения"""
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]
