"""
Генератор правил безопасности
"""

import os
from typing import List, Dict, Optional
from jinja2 import Environment, FileSystemLoader

from .models import NetworkPolicy, SecurityRule, ActionType

class PolicyGenerator:
    """Генератор конфигураций для различных платформ"""
    
    def __init__(self, template_dir: str = "configs/templates"):
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def generate_openwrt_config(self, policy: NetworkPolicy) -> str:
        """Генерация конфигурации для OpenWrt"""
        template = self.env.get_template('openwrt.j2')
        
        # Подготавливаем данные для шаблона
        zones = []
        for zone_name, zone in policy.zones.items():
            zones.append({
                'name': zone_name,
                'type': zone.zone_type.value,
                'ips': zone.ip_list,
                'description': zone.description
            })
        
        rules = []
        for rule in policy.rules:
            rules.append({
                'source': rule.source_zone,
                'dest': rule.destination_zone,
                'action': rule.action.value,
                'protocol': rule.protocol,
                'ports': rule.ports,
                'description': rule.description
            })
        
        return template.render(
            policy_name=policy.name,
            zones=zones,
            rules=rules
        )
    
    def generate_iptables_config(self, policy: NetworkPolicy) -> str:
        """Генерация iptables правил"""
        template = self.env.get_template('iptables.j2')
        
        # Формируем правила
        iptables_rules = []
        
        for rule in policy.rules:
            source_zone = policy.zones.get(rule.source_zone)
            dest_zone = policy.zones.get(rule.destination_zone)
            
            if source_zone and dest_zone:
                for source_ip in source_zone.ip_list:
                    for dest_ip in dest_zone.ip_list:
                        rule_text = self._create_iptables_rule(
                            source_ip, dest_ip, rule
                        )
                        iptables_rules.append(rule_text)
        
        return template.render(
            policy_name=policy.name,
            rules=iptables_rules
        )
    
    def _create_iptables_rule(self, src_ip: str, dst_ip: str, rule: SecurityRule) -> str:
        """Создать одну строку iptables правила"""
        parts = ["iptables -A FORWARD"]
        
        # Источник и назначение
        parts.append(f"-s {src_ip}")
        parts.append(f"-d {dst_ip}")
        
        # Протокол
        if rule.protocol != 'any':
            parts.append(f"-p {rule.protocol}")
            if rule.ports and rule.protocol in ['tcp', 'udp']:
                ports_str = ','.join(map(str, rule.ports))
                parts.append(f"--dport {ports_str}")
        
        # Действие
        action_map = {
            'allow': 'ACCEPT',
            'deny': 'DROP'
        }
        action = action_map.get(rule.action.value, 'DROP')
        parts.append(f"-j {action}")
        
        # Комментарий
        parts.append(f"-m comment --comment \"{rule.description}\"")
        
        return ' '.join(parts)
    
    def generate_windows_firewall(self, policy: NetworkPolicy) -> str:
        """Генерация PowerShell скрипта для Windows Firewall"""
        template = self.env.get_template('windows.ps1')
        
        # Подготавливаем правила
        firewall_rules = []
        
        for rule in policy.rules:
            source_zone = policy.zones.get(rule.source_zone)
            dest_zone = policy.zones.get(rule.destination_zone)
            
            if source_zone and dest_zone:
                for source_ip in source_zone.ip_list:
                    for dest_ip in dest_zone.ip_list:
                        firewall_rules.append({
                            'source_ip': source_ip,
                            'dest_ip': dest_ip,
                            'action': rule.action.value,
                            'protocol': rule.protocol.upper() if rule.protocol != 'any' else 'ANY',
                            'ports': rule.ports,
                            'description': rule.description
                        })
        
        return template.render(
            policy_name=policy.name,
            rules=firewall_rules
        )
    
    def export_policy(self, policy: NetworkPolicy, platform: str, output_file: str):
        """Экспорт политики в файл"""
        if platform.lower() == 'openwrt':
            config = self.generate_openwrt_config(policy)
        elif platform.lower() == 'iptables':
            config = self.generate_iptables_config(policy)
        elif platform.lower() == 'windows':
            config = self.generate_windows_firewall(policy)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
        
        # Создаем директорию, если не существует
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Сохраняем конфигурацию
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(config)
        
        return output_file