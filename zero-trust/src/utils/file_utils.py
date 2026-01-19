"""
Утилиты для работы с файлами
"""

import json
import yaml
import pickle
from typing import Any, Dict, Optional
from pathlib import Path
import hashlib
from datetime import datetime

from ..core.exceptions import FileSystemError

def save_to_file(data: Any, filepath: Path, format: str = 'json') -> bool:
    """
    Сохранить данные в файл
    
    Args:
        data: Данные для сохранения
        filepath: Путь к файлу
        format: Формат файла (json, yaml, pickle)
    
    Returns:
        True если успешно
    """
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'json':
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        elif format == 'yaml':
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
                
        elif format == 'pickle':
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
                
        else:
            raise FileSystemError(f"Неподдерживаемый формат: {format}")
        
        return True
        
    except Exception as e:
        raise FileSystemError(f"Ошибка сохранения файла {filepath}: {e}")

def load_from_file(filepath: Path, format: str = 'json') -> Any:
    """
    Загрузить данные из файла
    
    Args:
        filepath: Путь к файлу
        format: Формат файла (json, yaml, pickle)
    
    Returns:
        Загруженные данные
    """
    try:
        if not filepath.exists():
            raise FileSystemError(f"Файл не существует: {filepath}")
        
        if format == 'json':
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        elif format == 'yaml':
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
                
        elif format == 'pickle':
            with open(filepath, 'rb') as f:
                return pickle.load(f)
                
        else:
            raise FileSystemError(f"Неподдерживаемый формат: {format}")
        
    except Exception as e:
        raise FileSystemError(f"Ошибка загрузки файла {filepath}: {e}")

def get_file_hash(filepath: Path) -> str:
    """
    Получить хэш содержимого файла
    
    Args:
        filepath: Путь к файлу
    
    Returns:
        SHA256 хэш файла
    """
    try:
        hasher = hashlib.sha256()
        
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        
        return hasher.hexdigest()
        
    except Exception as e:
        raise FileSystemError(f"Ошибка вычисления хэша файла {filepath}: {e}")

def backup_file(file
