"""
Генератор автоматических правил безопасности
"""

from typing import List, Dict
import random

from ..core.models import NetworkPolicy, SecurityZone, ZoneType, Rule, ActionType, NetworkDevice

class RuleGenerator:
    """Генератор автоматических правил безопасности"""
    
    def __init__(self):
        self.best_practices = self._load_best_practices()
    
    def _load_best_practices(self) -> Dict:
        """Загрузить лучшие практики безопасности"""
        return {
            ZoneType.TRUSTED: {
                ZoneType.GUEST: {'action': 'deny', 'description': 'Блокировать гостей'},
                ZoneType.IOT: {'action': 'deny', 'description': 'Изолировать IoT'},
                ZoneType.DMZ: {'action': 'allow', 'description': 'Доступ к DMZ'},
            },
            ZoneType.IOT: {
                ZoneType.TRUSTED: {'action': 'deny', 'description': 'IoT изолировано'},
                ZoneType.GUEST: {'action': 'deny', 'description': 'IoT не для гостей'},
                ZoneType.SERVER: {'action': 'allow', 'description': 'Доступ к серверам'},
            },
            ZoneType.GUEST: {
                ZoneType.TRUSTED: {'action': 'deny', 'description': 'Гости изолированы'},
                ZoneType.IOT: {'action': 'deny', 'description': 'Нет доступа к IoT'},
                ZoneType.DMZ: {'action': 'allow', 'description': 'Доступ к интернету'},
            }
        }
    
    def generate_best_practice_rules(self, policy: NetworkPolicy) -> List[Rule]:
        """Сгенерировать правила на основе лучших практик"""
        generated_rules = []
        
        for src_zone_name, src_zone in policy.zones.items():
            for dst_zone_name, dst_zone in policy.zones.items():
                if src_zone_name == dst_zone_name:
                    continue
                
                # Проверяем лучшие практики для этой пары зон
                src_type = src_zone.zone_type
                dst_type = dst_zone.zone_type
                
                if src_type in self.best_practices and dst_type in self.best_practices[src_type]:
                    practice = self.best_practices[src_type][dst_type]
                    
                    rule = Rule(
                        source_zone=src_zone,
                        destination_zone=dst_zone,
                        action=ActionType(practice['action']),
                        description=practice['description']
                    )
                    
                    generated_rules.append(rule)
        
        return generated_rules
    
    def generate_device_based_rules(self, policy: NetworkPolicy) -> List[Rule]:
        """Сгенерировать правила на основе типов устройств"""
        generated_rules = []
        
        # Правила для IoT устройств
        iot_zones = [z for z in policy.zones.values() if z.zone_type == ZoneType.IOT]
        
        for iot_zone in iot_zones:
            for device in iot_zone.devices:
                # IoT устройствам разрешаем только необходимые порты
                if device.open_ports:
                    for port in device.open_ports:
                        # Правило для конкретного порта
                        rule = Rule(
                            source_zone=iot_zone,
                            destination_zone=iot_zone,
                            action=ActionType.ALLOW,
                            protocol="tcp",
                            destination_port=str(port),
                            description=f"Разрешить порт {port} для IoT устройства"
                        )
                        generated_rules.append(rule)
        
        return generated_rules
    
    def generate_segmentation_rules(self, policy: NetworkPolicy) -> List[Rule]:
        """Сгенерировать правила сегментации сети"""
        generated_rules = []
        
        zones = list(policy.zones.values())
        
        # Разрешаем все внутри зоны
        for zone in zones:
            rule = Rule(
                source_zone=zone,
                destination_zone=zone,
                action=ActionType.ALLOW,
                description=f"Разрешить трафик внутри зоны {zone.name}"
            )
            generated_rules.append(rule)
        
        # По умолчанию запрещаем все между зонами
        for i, src_zone in enumerate(zones):
            for j, dst_zone in enumerate(zones):
                if i != j:
                    rule = Rule(
                        source_zone=src_zone,
                        destination_zone=dst_zone,
                        action=ActionType.DENY,
                        description=f"Запретить трафик из {src_zone.name} в {dst_zone.name}"
                    )
                    generated_rules.append(rule)
        
        return generated_rules
    
    def generate_web_filtering_rules(self, policy: NetworkPolicy) -> List[Rule]:
        """Сгенерировать правила фильтрации веб-трафика"""
        generated_rules = []
        
        # Правила для гостевой сети
        guest_zones = [z for z in policy.zones.values() if z.zone_type == ZoneType.GUEST]
        
        for guest_zone in guest_zones:
            # Запретить торренты
            rule = Rule(
                source_zone=guest_zone,
                destination_zone=guest_zone,
                action=ActionType.DENY,
                protocol="tcp",
                destination_port="6881-6889",
                description="Блокировать торрент-трафик в гостевой сети"
            )
            generated_rules.append(rule)
            
            # Запретить небезопасные порты
            rule = Rule(
                source_zone=guest_zone,
                destination_zone=guest_zone,
                action=ActionType.DENY,
                protocol="tcp",
                destination_port="23,135-139,445",
                description="Блокировать небезопасные порты"
            )
            generated_rules.append(rule)
        
        return generated_rules
