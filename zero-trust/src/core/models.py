"""
Модели данных для ZeroTrust Inspector
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any
import json
import ipaddress

class DeviceType(Enum):
    ROUTER = "router"
    COMPUTER = "computer"
    PHONE = "phone"
    IOT = "iot"
    PRINTER = "printer"
    CAMERA = "camera"
    TV = "tv"
    NAS = "nas"
    UNKNOWN = "unknown"

class ZoneType(Enum):
    TRUSTED = "trusted"
    IOT = "iot"
    GUEST = "guest"
    SERVER = "server"
    DMZ = "dmz"
    CUSTOM = "custom"

class ActionType(Enum):
    ALLOW = "allow"
    DENY = "deny"

@dataclass
class NetworkDevice:
    """Сетевое устройство"""
    ip_address: str
    mac_address: Optional[str] = None
    hostname: Optional[str] = None
    device_type: DeviceType = DeviceType.UNKNOWN
    vendor: Optional[str] = None
    open_ports: List[int] = field(default_factory=list)
    os_info: Optional[str] = None
    risk_score: float = 0.5
    is_gateway: bool = False
    
    def __post_init__(self):
        """Валидация IP-адреса"""
        try:
            ipaddress.ip_address(self.ip_address)
        except ValueError:
            raise ValueError(f"Invalid IP address: {self.ip_address}")
    
    @property
    def display_name(self) -> str:
        """Имя для отображения"""
        if self.hostname and self.hostname != 'unknown':
            return self.hostname
        return self.ip_address
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертировать в словарь"""
        return {
            'ip_address': self.ip_address,
            'mac_address': self.mac_address,
            'hostname': self.hostname,
            'device_type': self.device_type.value,
            'vendor': self.vendor,
            'open_ports': self.open_ports,
            'os_info': self.os_info,
            'risk_score': self.risk_score,
            'is_gateway': self.is_gateway
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetworkDevice':
        """Создать из словаря"""
        return cls(
            ip_address=data['ip_address'],
            mac_address=data.get('mac_address'),
            hostname=data.get('hostname'),
            device_type=DeviceType(data.get('device_type', 'unknown')),
            vendor=data.get('vendor'),
            open_ports=data.get('open_ports', []),
            os_info=data.get('os_info'),
            risk_score=data.get('risk_score', 0.5),
            is_gateway=data.get('is_gateway', False)
        )

@dataclass
class SecurityZone:
    """Зона безопасности"""
    name: str
    zone_type: ZoneType
    description: str = ""
    devices: List[NetworkDevice] = field(default_factory=list)
    color: str = "#808080"
    position: tuple = (0, 0)  # Позиция на канвасе
    size: tuple = (200, 150)  # Размер зоны
    
    def __post_init__(self):
        """Установка цвета по типу зоны"""
        color_map = {
            ZoneType.TRUSTED: "#4CAF50",  # Зеленый
            ZoneType.IOT: "#FF9800",      # Оранжевый
            ZoneType.GUEST: "#9C27B0",    # Фиолетовый
            ZoneType.SERVER: "#2196F3",   # Синий
            ZoneType.DMZ: "#F44336",      # Красный
        }
        self.color = color_map.get(self.zone_type, self.color)
    
    def add_device(self, device: NetworkDevice):
        """Добавить устройство в зону"""
        if device not in self.devices:
            self.devices.append(device)
    
    def remove_device(self, device: NetworkDevice):
        """Удалить устройство из зоны"""
        if device in self.devices:
            self.devices.remove(device)
    
    @property
    def device_count(self) -> int:
        """Количество устройств в зоне"""
        return len(self.devices)
    
    @property
    def ip_list(self) -> List[str]:
        """Список IP-адресов устройств"""
        return [device.ip_address for device in self.devices]
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертировать в словарь"""
        return {
            'name': self.name,
            'zone_type': self.zone_type.value,
            'description': self.description,
            'devices': [device.to_dict() for device in self.devices],
            'color': self.color,
            'position': self.position,
            'size': self.size
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecurityZone':
        """Создать из словаря"""
        zone = cls(
            name=data['name'],
            zone_type=ZoneType(data['zone_type']),
            description=data.get('description', ''),
            color=data.get('color', '#808080'),
            position=tuple(data.get('position', (0, 0))),
            size=tuple(data.get('size', (200, 150)))
        )
        
        for device_data in data.get('devices', []):
            zone.devices.append(NetworkDevice.from_dict(device_data))
        
        return zone

@dataclass
class SecurityRule:
    """Правило безопасности"""
    source_zone: str
    destination_zone: str
    action: ActionType
    protocol: str = "any"
    ports: Optional[List[int]] = None
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертировать в словарь"""
        return {
            'source_zone': self.source_zone,
            'destination_zone': self.destination_zone,
            'action': self.action.value,
            'protocol': self.protocol,
            'ports': self.ports,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecurityRule':
        """Создать из словаря"""
        return cls(
            source_zone=data['source_zone'],
            destination_zone=data['destination_zone'],
            action=ActionType(data['action']),
            protocol=data.get('protocol', 'any'),
            ports=data.get('ports'),
            description=data.get('description', '')
        )

@dataclass
class NetworkPolicy:
    """Политика безопасности"""
    name: str
    description: str = ""
    zones: Dict[str, SecurityZone] = field(default_factory=dict)
    rules: List[SecurityRule] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_zone(self, zone: SecurityZone):
        """Добавить зону"""
        self.zones[zone.name] = zone
    
    def remove_zone(self, zone_name: str):
        """Удалить зону"""
        if zone_name in self.zones:
            del self.zones[zone_name]
            # Удаляем связанные правила
            self.rules = [
                rule for rule in self.rules
                if rule.source_zone != zone_name and rule.destination_zone != zone_name
            ]
    
    def add_rule(self, rule: SecurityRule):
        """Добавить правило"""
        if rule.source_zone in self.zones and rule.destination_zone in self.zones:
            self.rules.append(rule)
    
    def validate(self) -> List[str]:
        """Валидация политики"""
        errors = []
        
        if not self.zones:
            errors.append("Нет зон безопасности")
        
        for rule in self.rules:
            if rule.source_zone not in self.zones:
                errors.append(f"Правило ссылается на несуществующую зону: {rule.source_zone}")
            if rule.destination_zone not in self.zones:
                errors.append(f"Правило ссылается на несуществующую зону: {rule.destination_zone}")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертировать в словарь"""
        return {
            'name': self.name,
            'description': self.description,
            'zones': {name: zone.to_dict() for name, zone in self.zones.items()},
            'rules': [rule.to_dict() for rule in self.rules],
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetworkPolicy':
        """Создать из словаря"""
        policy = cls(
            name=data['name'],
            description=data.get('description', '')
        )
        
        if 'created_at' in data:
            policy.created_at = datetime.fromisoformat(data['created_at'])
        
        # Загружаем зоны
        for zone_name, zone_data in data.get('zones', {}).items():
            policy.zones[zone_name] = SecurityZone.from_dict(zone_data)
        
        # Загружаем правила
        for rule_data in data.get('rules', []):
            policy.rules.append(SecurityRule.from_dict(rule_data))
        
        return policy
    
    def save_to_file(self, filepath: str):
        """Сохранить в файл"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'NetworkPolicy':
        """Загрузить из файла"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)