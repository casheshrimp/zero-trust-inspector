"""
База данных отпечатков сетевых устройств
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import sqlite3
from datetime import datetime

from ..core.constants import ASSETS_DIR
from ..core.models import NetworkDevice, DeviceType

class FingerprintDatabase:
    """База данных для хранения и сопоставления отпечатков устройств"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or ASSETS_DIR / "fingerprints.db"
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица отпечатков устройств
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS device_fingerprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor TEXT NOT NULL,
                model TEXT,
                mac_prefix TEXT,
                common_ports TEXT,  # JSON список портов
                http_headers TEXT,  # JSON заголовки HTTP
                banners TEXT,       # JSON баннеры сервисов
                device_type TEXT,
                confidence REAL DEFAULT 0.8,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица известных уязвимостей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS known_vulnerabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cve_id TEXT UNIQUE,
                device_type TEXT,
                vendor TEXT,
                affected_versions TEXT,
                severity TEXT,
                description TEXT,
                mitigation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Индексы для ускорения поиска
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_mac_prefix ON device_fingerprints(mac_prefix)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_device_type ON device_fingerprints(device_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vendor ON device_fingerprints(vendor)')
        
        conn.commit()
        conn.close()
        
        # Загрузка начальных данных
        self._load_initial_data()
    
    def _load_initial_data(self):
        """Загрузка начальных данных в базу"""
        initial_fingerprints = [
            {
                "vendor": "Raspberry Pi",
                "mac_prefix": "B8:27:EB",
                "common_ports": [22, 80, 443],
                "device_type": "computer"
            },
            {
                "vendor": "Philips Hue",
                "model": "Bridge",
                "common_ports": [80, 443],
                "http_headers": {"Server": "hue"},
                "device_type": "iot"
            },
            {
                "vendor": "ASUS",
                "model": "Router",
                "common_ports": [80, 443, 22, 23],
                "device_type": "router"
            },
            {
                "vendor": "Synology",
                "model": "NAS",
                "common_ports": [5000, 5001],
                "device_type": "server"
            },
            {
                "vendor": "HP",
                "model": "Printer",
                "common_ports": [9100, 631, 80],
                "device_type": "printer"
            },
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for fp in initial_fingerprints:
            cursor.execute('''
                INSERT OR IGNORE INTO device_fingerprints 
                (vendor, model, mac_prefix, common_ports, device_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                fp["vendor"],
                fp.get("model"),
                fp.get("mac_prefix"),
                json.dumps(fp.get("common_ports", [])),
                fp["device_type"]
            ))
        
        conn.commit()
        conn.close()
    
    def match_device(self, device: NetworkDevice) -> Dict:
        """
        Найти совпадение для устройства в базе отпечатков
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        matches = []
        
        # Поиск по MAC-префиксу
        if device.mac_address:
            mac_prefix = ':'.join(device.mac_address.upper().split(':')[:3])
            cursor.execute(
                'SELECT * FROM device_fingerprints WHERE mac_prefix = ?',
                (mac_prefix,)
            )
            matches.extend(cursor.fetchall())
        
        # Поиск по открытым портам
        if device.open_ports:
            # Конвертируем порты в JSON для поиска
            for row in cursor.execute('SELECT * FROM device_fingerprints'):
                common_ports = json.loads(row['common_ports'])
                if set(common_ports).intersection(set(device.open_ports)):
                    matches.append(row)
        
        # Убираем дубликаты
        unique_matches = []
        seen_ids = set()
        for match in matches:
            if match['id'] not in seen_ids:
                unique_matches.append(dict(match))
                seen_ids.add(match['id'])
        
        conn.close()
        
        if unique_matches:
            # Возвращаем лучшее совпадение
            return max(unique_matches, key=lambda x: x.get('confidence', 0))
        
        return {}
    
    def add_fingerprint(self, vendor: str, device_type: str, **kwargs):
        """Добавить новый отпечаток в базу"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO device_fingerprints 
            (vendor, device_type, mac_prefix, common_ports, http_headers, banners, model, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            vendor,
            device_type,
            kwargs.get('mac_prefix'),
            json.dumps(kwargs.get('common_ports', [])),
            json.dumps(kwargs.get('http_headers', {})),
            json.dumps(kwargs.get('banners', {})),
            kwargs.get('model'),
            kwargs.get('confidence', 0.8)
        ))
        
        conn.commit()
        conn.close()
    
    def get_vulnerabilities(self, device_type: str = None, vendor: str = None) -> List[Dict]:
        """Получить известные уязвимости для типа устройств или производителя"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM known_vulnerabilities WHERE 1=1'
        params = []
        
        if device_type:
            query += ' AND device_type = ?'
            params.append(device_type)
        
        if vendor:
            query += ' AND vendor = ?'
            params.append(vendor)
        
        cursor.execute(query, params)
        vulnerabilities = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return vulnerabilities
