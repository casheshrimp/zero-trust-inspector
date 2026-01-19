"""
Тесты для модуля core
"""

import unittest
from datetime import datetime

from src.core.models import (
    NetworkDevice, SecurityZone, NetworkPolicy, Rule,
    ZoneType, DeviceType, ActionType
)

class TestModels(unittest.TestCase):
    """Тесты моделей данных"""
    
    def test_device_creation(self):
        """Тест создания устройства"""
        device = NetworkDevice(
            ip_address="192.168.1.10",
            mac_address="00:11:22:33:44:55",
            hostname="test-device",
            device_type=DeviceType.COMPUTER
        )
        
        self.assertEqual(device.ip_address, "192.168.1.10")
        self.assertEqual(device.device_type, DeviceType.COMPUTER)
    
    def test_zone_operations(self):
        """Тест операций с зонами"""
        zone = SecurityZone("TestZone", ZoneType.TRUSTED)
        device = NetworkDevice("192.168.1.10")
        
        zone.add_device(device)
        self.assertEqual(zone.device_count, 1)
        
        zone.remove_device("192.168.1.10")
        self.assertEqual(zone.device_count, 0)
    
    def test_policy_validation(self):
        """Тест валидации политики"""
        policy = NetworkPolicy("Test Policy")
        
        zone = SecurityZone("Trusted", ZoneType.TRUSTED)
        policy.add_zone(zone)
        
        self.assertTrue(policy.validate())
        
        # Добавляем правило с несуществующей зоной
        fake_zone = SecurityZone("Fake", ZoneType.CUSTOM)
        rule = Rule(fake_zone, zone, ActionType.ALLOW)
        policy.add_rule(rule)
        
        self.assertFalse(policy.validate())
    
    def test_rule_serialization(self):
        """Тест сериализации правил"""
        zone1 = SecurityZone("Src", ZoneType.TRUSTED)
        zone2 = SecurityZone("Dst", ZoneType.IOT)
        
        rule = Rule(
            source_zone=zone1,
            destination_zone=zone2,
            action=ActionType.DENY,
            protocol="tcp",
            destination_port="80",
            description="Блокировать HTTP"
        )
        
        rule_dict = rule.to_dict()
        self.assertEqual(rule_dict['action'], "deny")
        self.assertEqual(rule_dict['protocol'], "tcp")

class TestEnums(unittest.TestCase):
    """Тесты перечислений"""
    
    def test_zone_types(self):
        """Тест типов зон"""
        self.assertEqual(ZoneType.TRUSTED.value, "trusted")
        self.assertEqual(ZoneType.IOT.value, "iot")
    
    def test_device_types(self):
        """Тест типов устройств"""
        self.assertEqual(DeviceType.ROUTER.value, "router")
        self.assertEqual(DeviceType.IOT.value, "iot")
    
    def test_action_types(self):
        """Тест типов действий"""
        self.assertEqual(ActionType.ALLOW.value, "allow")
        self.assertEqual(ActionType.DENY.value, "deny")

if __name__ == '__main__':
    unittest.main()
