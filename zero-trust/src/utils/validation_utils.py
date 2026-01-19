"""
Утилиты для валидации данных
"""

import re
from typing import List, Dict, Any
from ipaddress import IPv4Address, IPv4Network

from ..core.exceptions import PolicyValidationError

def validate_policy_data(data: Dict[str, Any]) -> List[str]:
    """Валидация данных политики"""
    errors = []
    
    # Проверка обязательных полей
    required_fields = ['name', 'zones']
    for field in required_fields:
        if field not in data:
            errors.append(f"Отсутствует обязательное поле: {field}")
    
    # Проверка имени политики
    if 'name' in data:
        name = data['name']
        if not name or len(name.strip()) == 0:
            errors.append("Имя политики не может быть пустым")
        elif len(name) > 100:
            errors.append("Имя политики слишком длинное (макс. 100 символов)")
    
    # Проверка зон
    if 'zones' in data and isinstance(data['zones'], list):
        if len(data['zones']) == 0:
            errors.append("Политика должна содержать хотя бы одну зону")
        
        zone_names = set()
        for zone in data['zones']:
            if 'name' not in zone:
                errors.append("Зона должна иметь имя")
            elif zone['name'] in zone_names:
                errors.append(f"Дублирующееся имя зоны: {zone['name']}")
            else:
                zone_names.add(zone['name'])
    
    return errors

def validate_ip_range(ip_range: str) -> bool:
    """Валидация диапазона IP-адресов"""
    try:
        # Поддерживаемые форматы:
        # 192.168.1.0/24
        # 192.168.1.1-192.168.1.10
        # 192.168.1.*
        
        if '/' in ip_range:
            # CIDR нотация
            IPv4Network(ip_range, strict=False)
            return True
        elif '-' in ip_range:
            # Диапазон
            start_ip, end_ip = ip_range.split('-')
            IPv4Address(start_ip.strip())
            IPv4Address(end_ip.strip())
            return True
        elif '*' in ip_range:
            # Шаблон с маской
            parts = ip_range.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                if part != '*' and not (0 <= int(part) <= 255):
                    return False
            return True
        else:
            # Одиночный IP
            IPv4Address(ip_range)
            return True
            
    except Exception:
        return False

def validate_port(port: Any) -> bool:
    """Валидация порта"""
    try:
        port_int = int(port)
        return 0 <= port_int <= 65535
    except (ValueError, TypeError):
        return False

def validate_port_range(port_range: str) -> bool:
    """Валидация диапазона портов"""
    try:
        if ':' in port_range:
            start_port, end_port = port_range.split(':')
            return validate_port(start_port) and validate_port(end_port)
        else:
            return validate_port(port_range)
    except Exception:
        return False

def validate_mac_address(mac: str) -> bool:
    """Валидация MAC-адреса"""
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return bool(re.match(pattern, mac))

def sanitize_input(text: str, max_length: int = 500) -> str:
    """Очистка пользовательского ввода"""
    if not text:
        return text
    
    # Убираем потенциально опасные символы
    sanitized = text.strip()
    sanitized = re.sub(r'[<>"\'&;]', '', sanitized)
    
    # Обрезаем до максимальной длины
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized
