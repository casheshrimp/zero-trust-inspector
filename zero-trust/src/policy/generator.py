"""
Генератор правил безопасности
"""

import os
from typing import Dict, List, Optional
from jinja2 import Environment, FileSystemLoader, Template

from ..core.models import NetworkPolicy, Rule, ActionType, ProtocolType

class PolicyGenerator:
    """Генератор правил безопасности для различных платформ"""
    
    def __init__(self, template_dir: str = None):
        if template_dir is None:
            # По умолчанию используем директорию с шаблонами
            template_dir = os.path.join(
                os.path.dirname(__file__), 
                '../../../configs/templates'
            )
        
        # Создаем окружение Jinja2
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Регистрируем фильтры
        self.env.filters['action_to_str'] = self._action_to_str
        self.env.filters['protocol_to_str'] = self._protocol_to_str
    
    def _action_to_str(self, action: ActionType) -> str:
        """Конвертировать действие в строку"""
        action_map = {
            ActionType.ALLOW: "allow",
            ActionType.DENY: "deny",
            ActionType.LIMIT: "limit"
        }
        return action_map.get(action, "deny")
    
    def _protocol_to_str(self, protocol: ProtocolType) -> str:
        """Конвертировать протокол в строку"""
        protocol_map = {
            ProtocolType.TCP: "tcp",
            ProtocolType.UDP: "udp",
            ProtocolType.ICMP: "icmp",
            ProtocolType.ANY: "any"
        }
        return protocol_map.get(protocol, "any")
    
    def generate_openwrt_config(self, policy: NetworkPolicy) -> str:
        """Сгенерировать конфигурацию для OpenWrt"""
        template = self.env.get_template('openwrt.j2')
        
        # Подготавливаем данные для шаблона
        zones_data = []
        rules_data = []
        
        for zone_name, zone in policy.zones.items():
            # Получаем список IP-адресов устройств в зоне
            ip_addresses = [device.ip_address for device in zone.devices]
            
            zones_data.append({
                'name': zone_name,
                'type': zone.zone_type.value,
                'description': zone.description,
                'ip_addresses': ip_addresses,
                'color': zone.color
            })
        
        for rule in policy.rules:
            if rule.enabled:
                rules_data.append({
                    'source_zone': rule.source_zone,
                    'dest_zone': rule.destination_zone,
                    'action': rule.action,
                    'protocol': rule.protocol,
                    'port': rule.port,
                    'description': rule.description
                })
        
        context = {
            'policy_name': policy.name,
            'zones': zones_data,
            'rules': rules_data,
            'created_at': policy.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return template.render(context)
    
    def generate_windows_firewall_config(self, policy: NetworkPolicy) -> str:
        """Сгенерировать PowerShell скрипт для Windows Firewall"""
        template = self.env.get_template('windows_firewall.j2')
        
        # Подготавливаем данные
        zones_data = {}
        rules_data = []
        
        for zone_name, zone in policy.zones.items():
            zones_data[zone_name] = {
                'ips': [device.ip_address for device in zone.devices],
                'description': zone.description
            }
        
        for rule in policy.rules:
            if rule.enabled:
                # Для Windows Firewall нужны конкретные правила
                source_zone = policy.zones.get(rule.source_zone)
                dest_zone = policy.zones.get(rule.destination_zone)
                
                if source_zone and dest_zone:
                    for source_device in source_zone.devices:
                        for dest_device in dest_zone.devices:
                            rules_data.append({
                                'source_ip': source_device.ip_address,
                                'dest_ip': dest_device.ip_address,
                                'action': rule.action,
                                'protocol': rule.protocol,
                                'port': rule.port,
                                'description': f"{rule.description} ({source_device.ip_address} -> {dest_device.ip_address})"
                            })
        
        context = {
            'policy_name': policy.name,
            'zones': zones_data,
            'rules': rules_data
        }
        
        return template.render(context)
    
    def generate_iptables_config(self, policy: NetworkPolicy) -> str:
        """Сгенерировать скрипт iptables"""
        template = self.env.get_template('iptables.j2')
        
        # Создаем наборы IP-адресов для каждой зоны
        zone_ips = {}
        for zone_name, zone in policy.zones.items():
            zone_ips[zone_name] = [device.ip_address for device in zone.devices]
        
        # Формируем правила
        iptables_rules = []
        
        for rule in policy.rules:
            if rule.enabled:
                # Добавляем правило для всех комбинаций IP-адресов
                for source_ip in zone_ips.get(rule.source_zone, []):
                    for dest_ip in zone_ips.get(rule.destination_zone, []):
                        rule_text = self._create_iptables_rule(
                            source_ip, dest_ip, rule
                        )
                        if rule_text:
                            iptables_rules.append(rule_text)
        
        context = {
            'policy_name': policy.name,
            'rules': iptables_rules,
            'zones': zone_ips
        }
        
        return template.render(context)
    
    def _create_iptables_rule(self, source_ip: str, dest_ip: str, rule: Rule) -> str:
        """Создать одну строку правила iptables"""
        # Базовое правило
        rule_parts = ["iptables -A FORWARD"]
        
        # Добавляем критерии
        rule_parts.append(f"-s {source_ip}")
        rule_parts.append(f"-d {dest_ip}")
        
        # Протокол и порт
        if rule.protocol != ProtocolType.ANY:
            rule_parts.append(f"-p {rule.protocol.value}")
            if rule.port and rule.protocol in [ProtocolType.TCP, ProtocolType.UDP]:
                rule_parts.append(f"--dport {rule.port}")
        
        # Действие
        action_map = {
            ActionType.ALLOW: "ACCEPT",
            ActionType.DENY: "DROP",
            ActionType.LIMIT: "ACCEPT -m limit --limit 10/min"
        }
        rule_parts.append(f"-j {action_map.get(rule.action, 'DROP')}")
        
        # Комментарий
        rule_parts.append(f"-m comment --comment \"{rule.description}\"")
        
        return " ".join(rule_parts)
    
    def export_config(self, policy: NetworkPolicy, platform: str, output_file: str):
        """Экспортировать конфигурацию в файл"""
        config = ""
        
        if platform.lower() == 'openwrt':
            config = self.generate_openwrt_config(policy)
        elif platform.lower() == 'windows':
            config = self.generate_windows_firewall_config(policy)
        elif platform.lower() in ['iptables', 'linux']:
            config = self.generate_iptables_config(policy)
        else:
            raise ValueError(f"Неподдерживаемая платформа: {platform}")
        
        # Сохраняем в файл
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(config)
        
        return output_file
