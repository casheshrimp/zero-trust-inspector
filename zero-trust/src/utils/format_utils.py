"""
Утилиты для форматирования данных
"""

import json
from typing import Any, Dict, List
from datetime import datetime
import humanize

def format_file_size(size_bytes: int) -> str:
    """Форматировать размер файла в читаемый вид"""
    return humanize.naturalsize(size_bytes, binary=True)

def format_timestamp(timestamp: datetime, format_str: str = None) -> str:
    """Форматировать timestamp"""
    if format_str:
        return timestamp.strftime(format_str)
    return humanize.naturaltime(datetime.now() - timestamp)

def format_ip_list(ips: List[str]) -> str:
    """Форматировать список IP-адресов"""
    if not ips:
        return ""
    
    if len(ips) <= 3:
        return ", ".join(ips)
    
    return f"{ips[0]}, {ips[1]}, ... и еще {len(ips) - 2}"

def format_json(data: Any, indent: int = 2) -> str:
    """Красиво отформатировать JSON"""
    return json.dumps(data, indent=indent, ensure_ascii=False, default=str)

def format_risk_score(score: float) -> Dict:
    """Форматировать оценку риска с цветом"""
    if score >= 0.8:
        return {"text": "Высокий", "color": "#ff4444", "score": score}
    elif score >= 0.5:
        return {"text": "Средний", "color": "#ffaa00", "score": score}
    elif score >= 0.3:
        return {"text": "Низкий", "color": "#44ff44", "score": score}
    else:
        return {"text": "Минимальный", "color": "#00aa00", "score": score}

def format_device_type(device_type: str) -> str:
    """Форматировать тип устройства на русском"""
    type_map = {
        "computer": "Компьютер",
        "phone": "Телефон",
        "tablet": "Планшет",
        "iot": "Умное устройство",
        "printer": "Принтер",
        "router": "Роутер",
        "switch": "Свитч",
        "camera": "Камера",
        "unknown": "Неизвестно",
    }
    return type_map.get(device_type, device_type)

def format_port_list(ports: List[int]) -> str:
    """Форматировать список портов"""
    if not ports:
        return "Нет открытых портов"
    
    if len(ports) > 5:
        return f"{', '.join(map(str, ports[:5]))}... (всего {len(ports)})"
    
    return ', '.join(map(str, ports))

def format_time_delta(seconds: int) -> str:
    """Форматировать разницу во времени"""
    return humanize.naturaldelta(seconds)
