"""
Набор тестов для валидации политик
"""

import unittest
from typing import List, Dict
from datetime import datetime

from ..core.models import NetworkPolicy, SecurityZone, ZoneType, Rule, ActionType, NetworkDevice

class TestSuite(unittest.TestCase):
    """Набор тестов для валидации политик безопасности"""
    
    def setUp(self):
        """Настройка тестовой политики"""
        self.policy = NetworkPolicy(
            name="Test Policy",
            description="Тестовая политика для валидации"
        )
        
        # Создаем тестовые зоны
        zones = [
            SecurityZone("Trusted", ZoneType.TRUSTED),
            SecurityZone("IoT", ZoneType.IOT),
            SecurityZone("Guests", ZoneType.GUEST),
        ]
        
        for zone in zones:
            self.policy.add_zone(zone)
            
            # Добавляем тестовые устройства в зоны
            for i in range(2):
                device = NetworkDevice(
                    ip_address=f"192.168.1.{10 + i}",
                    hostname=f"Device_{zone.name}_{i}",
                    device_type="computer" if zone.name == "Trusted" else "iot"
                )
                zone.add_device(device)
        
        # Добавляем правила
        self.policy.add_rule(Rule(
            source_zone=self.policy.zones["Trusted"],
            destination_zone=self.policy.zones["IoT"],
            action=ActionType.DENY,
            description="Блокировка IoT из Trusted"
        ))
    
    def test_policy_validation(self):
        """Тест валидации политики"""
        self.assertTrue(self.policy.validate())
        
        # Проверка наличия всех зон в правилах
        for rule in self.policy.rules:
            self.assertIn(rule.source_zone.name, self.policy.zones)
            self.assertIn(rule.destination_zone.name, self.policy.zones)
    
    def test_zone_isolation(self):
        """Тест изоляции зон"""
        # Проверяем, что между Trusted и IoT есть правило DENY
        trust_to_iot_rules = self.policy.get_rules_between("Trusted", "IoT")
        self.assertTrue(len(trust_to_iot_rules) > 0)
        
        has_deny_rule = any(
            rule.action == ActionType.DENY 
            for rule in trust_to_iot_rules
        )
        self.assertTrue(has_deny_rule, "Должно быть правило DENY между Trusted и IoT")
    
    def test_device_count(self):
        """Тест подсчета устройств"""
        for zone_name, zone in self.policy.zones.items():
            self.assertEqual(zone.device_count, 2, 
                           f"В зоне {zone_name} должно быть 2 устройства")
    
    def test_rule_consistency(self):
        """Тест согласованности правил"""
        # Проверяем, что нет противоречивых правил
        rules_by_pair = {}
        
        for rule in self.policy.rules:
            key = (rule.source_zone.name, rule.destination_zone.name)
            if key not in rules_by_pair:
                rules_by_pair[key] = []
            rules_by_pair[key].append(rule.action)
        
        # В каждой паре зон не должно быть одновременно ALLOW и DENY
        for pair, actions in rules_by_pair.items():
            has_allow = ActionType.ALLOW in actions
            has_deny = ActionType.DENY in actions
            
            self.assertFalse(
                has_allow and has_deny,
                f"Конфликт правил в паре {pair}: есть и ALLOW, и DENY"
            )
    
    def test_empty_zone_detection(self):
        """Тест обнаружения пустых зон"""
        # Добавляем пустую зону
        empty_zone = SecurityZone("Empty", ZoneType.CUSTOM)
        self.policy.add_zone(empty_zone)
        
        # Проверяем, что зона действительно пуста
        self.assertEqual(empty_zone.device_count, 0)
        
        # Проверяем, что в политике есть эта зона
        self.assertIn("Empty", self.policy.zones)

def run_tests():
    """Запустить все тесты"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return {
        'tests_run': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'success': result.wasSuccessful(),
        'timestamp': datetime.now().isoformat()
    }

if __name__ == '__main__':
    results = run_tests()
    print(f"\nРезультаты тестирования:")
    print(f"Тестов выполнено: {results['tests_run']}")
    print(f"Ошибок: {results['errors']}")
    print(f"Провалов: {results['failures']}")
    print(f"Статус: {'УСПЕХ' if results['success'] else 'ПРОВАЛ'}")
