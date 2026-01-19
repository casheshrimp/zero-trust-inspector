"""
Движок обработки правил безопасности
"""

from typing import List, Dict, Optional
from pathlib import Path
import jinja2

from ..core.models import NetworkPolicy, Rule, SecurityZone
from ..core.exceptions import RuleGenerationError

class PolicyEngine:
    """Движок для обработки и генерации правил безопасности"""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = templates_dir or Path(__file__).parent / "templates"
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.templates_dir),
            autoescape=jinja2.select_autoescape()
        )
    
    def generate_firewall_rules(self, policy: NetworkPolicy, 
                               target_platform: str = "mikrotik") -> str:
        """
        Сгенерировать правила брандмауэра для целевой платформы
        
        Args:
            policy: Политика безопасности
            target_platform: Целевая платформа (mikrotik, ubiquiti, iptables)
        
        Returns:
            Сгенерированные правила в текстовом формате
        """
        try:
            # Загружаем шаблон для целевой платформы
            template_file = f"{target_platform}.j2"
            template = self.template_env.get_template(template_file)
            
            # Подготавливаем данные для шаблона
            template_data = {
                'policy': policy,
                'zones': list(policy.zones.values()),
                'rules': policy.rules,
                'generated_at': '{{ now }}'
            }
            
            # Рендерим шаблон
            return template.render(template_data)
            
        except jinja2.TemplateNotFound:
            raise RuleGenerationError(
                f"Шаблон для платформы '{target_platform}' не найден"
            )
        except Exception as e:
            raise RuleGenerationError(f"Ошибка генерации правил: {e}")
    
    def optimize_rules(self, policy: NetworkPolicy) -> NetworkPolicy:
        """Оптимизировать правила политики"""
        # Создаем копию политики
        optimized_policy = NetworkPolicy(
            name=f"{policy.name} (оптимизированная)",
            description=policy.description
        )
        
        # Копируем зоны
        for zone_name, zone in policy.zones.items():
            optimized_policy.add_zone(zone)
        
        # Оптимизируем правила
        optimized_rules = self._merge_rules(policy.rules)
        for rule in optimized_rules:
            optimized_policy.add_rule(rule)
        
        return optimized_policy
    
    def _merge_rules(self, rules: List[Rule]) -> List[Rule]:
        """Объединить дублирующиеся и противоречивые правила"""
        merged_rules = []
        rules_by_pair = {}
        
        # Группируем правила по парам зон
        for rule in rules:
            key = (rule.source_zone.name, rule.destination_zone.name)
            if key not in rules_by_pair:
                rules_by_pair[key] = []
            rules_by_pair[key].append(rule)
        
        # Объединяем правила в каждой паре
        for pair, rule_list in rules_by_pair.items():
            # Если есть правило DENY, оно имеет приоритет
            has_deny = any(r.action.value == 'deny' for r in rule_list)
            
            if has_deny:
                # Берем первое правило DENY
                deny_rule = next(r for r in rule_list if r.action.value == 'deny')
                merged_rules.append(deny_rule)
            else:
                # Берем первое правило ALLOW
                allow_rule = next(r for r in rule_list if r.action.value == 'allow')
                merged_rules.append(allow_rule)
        
        return merged_rules
    
    def validate_rule_conflicts(self, rules: List[Rule]) -> List[Dict]:
        """Проверить конфликты правил"""
        conflicts = []
        
        # Проверяем все пары правил
        for i in range(len(rules)):
            for j in range(i + 1, len(rules)):
                rule1 = rules[i]
                rule2 = rules[j]
                
                if self._are_rules_conflicting(rule1, rule2):
                    conflicts.append({
                        'rule1': rule1.description or f"Правило {i}",
                        'rule2': rule2.description or f"Правило {j}",
                        'conflict': 'Правила противоречат друг другу'
                    })
        
        return conflicts
    
    def _are_rules_conflicting(self, rule1: Rule, rule2: Rule) -> bool:
        """Проверить, конфликтуют ли два правила"""
        # Правила конфликтуют если:
        # 1. Они между одними и теми же зонами
        # 2. Они имеют противоположные действия (ALLOW vs DENY)
        # 3. Они применяются к одному порту/протоколу
        
        same_zones = (
            rule1.source_zone.name == rule2.source_zone.name and
            rule1.destination_zone.name == rule2.destination_zone.name
        )
        
        opposite_actions = (
            (rule1.action.value == 'allow' and rule2.action.value == 'deny') or
            (rule1.action.value == 'deny' and rule2.action.value == 'allow')
        )
        
        same_protocol = (
            rule1.protocol == rule2.protocol or
            rule1.protocol is None or
            rule2.protocol is None
        )
        
        same_ports = (
            rule1.destination_port == rule2.destination_port or
            rule1.destination_port is None or
            rule2.destination_port is None
        )
        
        return same_zones and opposite_actions and same_protocol and same_ports
