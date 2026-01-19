"""
Классификация устройств на основе различных признаков
"""

import re
from typing import Dict, Optional
import json
from pathlib import Path

from src.core.models import NetworkDevice, DeviceType
from src.core.constants import ASSETS_DIR
from src.core.exceptions import DeviceClassificationError

class DeviceClassifier:
    """Классификатор сетевых устройств"""
    
    def __init__(self):
        self.oui_db = self._load_oui_database()
        self.fingerprints = self._load_fingerprints()
        self.rules = self._get_classification_rules()
    
    def _load_oui_database(self) -> Dict[str, str]:
        """
        Загрузить базу данных OUI (Organizationally Unique Identifier)
        MAC-адреса: первые 3 байта определяют производителя
        """
        oui_file = ASSETS_DIR / "oui_database.json"
        
        if oui_file.exists():
            with open(oui_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Минимальная база для начала работы
        return {
            "00:11:22": "Cisco Systems",
            "00:50:56": "VMware",
            "00:0C:29": "VMware",
            "00:1A:2B": "ASUSTek",
            "00:1D:0F": "TP-Link",
            "00:26:18": "Raspberry Pi",
            "00:26:5A": "Apple",
            "00:50:F1": "Microsoft",
            "00:E0:4C": "Realtek",
            "08:00:27": "VirtualBox",
            "0C:4D:E9": "Apple",
            "18:68:CB": "Xiaomi",
            "28:6C:07": "Philips",
            "34:CE:00": "TP-Link",
            "50:C7:BF": "TP-Link",
            "74:AC:5F": "Qingdao",
            "84:0D:8E": "TP-Link",
            "A4:50:46": "Xiaomi",
            "B8:27:EB": "Raspberry Pi",
            "CC:46:D6": "Cisco",
            "D8:BB:2C": "Apple",
            "E4:8B:7F": "Xiaomi",
            "F0:9F:C2": "Ubiquiti",
        }
    
    def _load_fingerprints(self) -> Dict:
        """Загрузить отпечатки устройств"""
        fingerprints_file = ASSETS_DIR / "device_fingerprints.json"
        
        if fingerprints_file.exists():
            with open(fingerprints_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "printers": {
                "ports": [9100, 515, 631],
                "keywords": ["printer", "print", "hp", "epson", "canon", "brother"]
            },
            "cameras": {
                "ports": [80, 554, 37777],
                "keywords": ["camera", "dvr", "nvr", "hikvision", "dahua"]
            },
            "iot": {
                "ports": [80, 8080, 1883],
                "keywords": ["iot", "smart", "philips hue", "xiaomi", "yeelight"]
            },
            "routers": {
                "ports": [53, 80, 443, 22, 23],
                "keywords": ["router", "gateway", "asus", "tp-link", "mikrotik"]
            }
        }
    
    def _get_classification_rules(self) -> Dict:
        """Правила классификации"""
        return {
            DeviceType.ROUTER: [
                lambda d: self._check_ports(d, [53, 67, 68]),  # DNS, DHCP
                lambda d: d.ip_address.endswith('.1') or d.ip_address.endswith('.254'),
                lambda d: self._check_vendor_keywords(d, ['cisco', 'mikrotik', 'asus', 'tp-link', 'ubiquiti']),
            ],
            DeviceType.COMPUTER: [
                lambda d: self._check_ports(d, [22, 3389, 445, 139]),  # SSH, RDP, SMB
                lambda d: self._check_vendor_keywords(d, ['microsoft', 'apple', 'dell', 'hp', 'lenovo']),
                lambda d: len(d.open_ports) > 5,  # Много открытых портов
            ],
            DeviceType.PHONE: [
                lambda d: self._check_vendor_keywords(d, ['apple', 'samsung', 'xiaomi', 'huawei']),
                lambda d: self._check_ports(d, [62078, 5353]),  # iOS/Android порты
            ],
            DeviceType.IOT: [
                lambda d: self._check_ports(d, [80]) and len(d.open_ports) <= 3,
                lambda d: self._check_vendor_keywords(d, ['philips', 'xiaomi', 'yeelight', 'smart']),
                lambda d: 'camera' in str(d.hostname).lower() if d.hostname else False,
            ],
            DeviceType.PRINTER: [
                lambda d: self._check_ports(d, [9100, 515, 631]),
                lambda d: self._check_vendor_keywords(d, ['hp', 'epson', 'canon', 'brother']),
            ],
            DeviceType.CAMERA: [
                lambda d: self._check_ports(d, [80, 554, 37777]),
                lambda d: self._check_vendor_keywords(d, ['hikvision', 'dahua', 'camera']),
            ],
        }
    
    def classify_device(self, device: NetworkDevice) -> DeviceType:
        """
        Классифицировать устройство на основе множества признаков
        """
        if not device.mac_address:
            return self._classify_by_ports(device)
        
        # 1. Определяем производителя по MAC
        vendor = self.get_vendor_from_mac(device.mac_address)
        if vendor:
            device.vendor = vendor
        
        # 2. Пробуем классифицировать по правилам
        for device_type, rules in self.rules.items():
            for rule in rules:
                try:
                    if rule(device):
                        return device_type
                except Exception:
                    continue
        
        # 3. Если не удалось, классифицируем по портам
        return self._classify_by_ports(device)
    
    def get_vendor_from_mac(self, mac: str) -> Optional[str]:
        """
        Определить производителя по MAC-адресу
        """
        if not mac:
            return None
        
        # Нормализуем MAC-адрес
        mac = mac.upper().replace('-', ':')
        
        # Берем первые 3 байта (OUI)
        oui = ':'.join(mac.split(':')[:3])
        
        return self.oui_db.get(oui)
    
    def _classify_by_ports(self, device: NetworkDevice) -> DeviceType:
        """Классификация по открытым портам"""
        if not device.open_ports:
            return DeviceType.UNKNOWN
        
        # Проверяем отпечатки
        for device_type, fingerprint in self.fingerprints.items():
            if self._check_ports(device, fingerprint.get('ports', [])):
                # Дополнительная проверка по ключевым словам
                if device.hostname:
                    for keyword in fingerprint.get('keywords', []):
                        if keyword in device.hostname.lower():
                            # Маппинг строки на DeviceType enum
                            type_map = {
                                'printers': DeviceType.PRINTER,
                                'cameras': DeviceType.CAMERA,
                                'iot': DeviceType.IOT,
                                'routers': DeviceType.ROUTER,
                            }
                            return type_map.get(device_type, DeviceType.UNKNOWN)
        
        # Эвристики на основе портов
        ports = set(device.open_ports)
        
        if 9100 in ports:
            return DeviceType.PRINTER
        elif 3389 in ports:
            return DeviceType.COMPUTER
        elif 22 in ports and 445 in ports:
            return DeviceType.COMPUTER
        elif 80 in ports and len(ports) <= 3:
            return DeviceType.IOT
        elif {53, 67, 68}.intersection(ports):
            return DeviceType.ROUTER
        
        return DeviceType.UNKNOWN
    
    def _check_ports(self, device: NetworkDevice, target_ports: list) -> bool:
        """Проверить, содержит ли устройство указанные порты"""
        return any(port in device.open_ports for port in target_ports)
    
    def _check_vendor_keywords(self, device: NetworkDevice, keywords: list) -> bool:
        """Проверить производителя на ключевые слова"""
        if not device.vendor:
            return False
        
        vendor_lower = device.vendor.lower()
        return any(keyword in vendor_lower for keyword in keywords)
