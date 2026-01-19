"""
Валидатор политик безопасности
"""

import subprocess
import socket
import threading
import time
from typing import List, Dict, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from src.core.models import NetworkPolicy, Rule, ActionType, SecurityZone
from src.core.exceptions import PolicyValidationError

class PolicyValidator:
    """Валидатор для проверки корректности политик безопасности"""
    
    def __init__(self):
        self.test_results = []
        self.current_test = None
        self.is_testing = False
        
    def validate_policy(self, policy: NetworkPolicy, 
                       test_types: List[str] = None,
                       callback: Optional[Callable] = None) -> Dict:
        """
        Провести валидацию политики безопасности
        
        Args:
            policy: Политика для валидации
            test_types: Типы тестов для выполнения
            callback: Функция обратного вызова для прогресса
        
        Returns:
            Словарь с результатами тестирования
        """
        if test_types is None:
            test_types = ['connectivity', 'isolation', 'performance']
        
        self.is_testing = True
        self.test_results = []
        
        try:
            results = {
                'policy_name': policy.name,
                'test_start': datetime.now().isoformat(),
                'tests': {},
                'summary': {}
            }
            
            # Выполняем тесты
            test_methods = {
                'connectivity': self.test_connectivity,
                'isolation': self.test_zone_isolation,
                'performance': self.test_performance,
                'rule_validation': self.test_rule_validation,
            }
            
            for test_type in test_types:
                if test_type in test_methods and callback:
                    callback('test_started', f"Начинается тест: {test_type}", 0)
                
                if test_type in test_methods:
                    test_result = test_methods[test_type](policy)
                    results['tests'][test_type] = test_result
                    
                    if callback:
                        progress = int((len(results['tests']) / len(test_types)) * 100)
                        callback('test_completed', f"Тест {test_type} завершен", progress)
            
            # Формируем сводку
            results['summary'] = self._generate_summary(results['tests'])
            results['test_end'] = datetime.now().isoformat()
            
            self.test_results.append(results)
            self.is_testing = False
            
            if callback:
                callback('validation_complete', "Валидация завершена", 100)
            
            return results
            
        except Exception as e:
            self.is_testing = False
            raise PolicyValidationError(f"Ошибка валидации: {e}")
    
    def test_connectivity(self, policy: NetworkPolicy) -> Dict:
        """Тест базовой связности внутри зон"""
        results = {
            'name': 'Проверка связности',
            'description': 'Проверка доступности устройств внутри зон',
            'tests': [],
            'passed': 0,
            'failed': 0,
            'skipped': 0,
        }
        
        for zone_name, zone in policy.zones.items():
            if len(zone.devices) < 2:
                results['skipped'] += 1
                results['tests'].append({
                    'zone': zone_name,
                    'status': 'skipped',
                    'reason': 'Недостаточно устройств для теста'
                })
                continue
            
            # Берем первые два устройства из зоны для теста
            test_devices = zone.devices[:2]
            
            test_result = {
                'zone': zone_name,
                'devices': [d.ip_address for d in test_devices],
                'tests': []
            }
            
            # Проверяем ping между устройствами
            try:
                ping_result = self._ping_test(
                    test_devices[0].ip_address,
                    test_devices[1].ip_address
                )
                
                test_result['tests'].append({
                    'type': 'ping',
                    'source': test_devices[0].ip_address,
                    'target': test_devices[1].ip_address,
                    'result': ping_result,
                    'expected': True,
                    'status': 'passed' if ping_result else 'failed'
                })
                
                if ping_result:
                    results['passed'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                test_result['tests'].append({
                    'type': 'ping',
                    'source': test_devices[0].ip_address,
                    'target': test_devices[1].ip_address,
                    'result': False,
                    'error': str(e),
                    'status': 'error'
                })
                results['failed'] += 1
            
            results['tests'].append(test_result)
        
        return results
    
    def test_zone_isolation(self, policy: NetworkPolicy) -> Dict:
        """Тест изоляции между зонами"""
        results = {
            'name': 'Проверка изоляции зон',
            'description': 'Проверка блокировки трафика между зонами',
            'tests': [],
            'passed': 0,
            'failed': 0,
            'skipped': 0,
        }
        
        zone_names = list(policy.zones.keys())
        
        for i, zone1_name in enumerate(zone_names):
            for j, zone2_name in enumerate(zone_names):
                if i >= j:  # Чтобы не дублировать тесты
                    continue
                
                zone1 = policy.zones[zone1_name]
                zone2 = policy.zones[zone2_name]
                
                if not zone1.devices or not zone2.devices:
                    results['skipped'] += 1
                    continue
                
                # Берем по одному устройству из каждой зоны
                device1 = zone1.devices[0]
                device2 = zone2.devices[0]
                
                # Проверяем, должно ли быть соединение заблокировано
                should_block = True
                for rule in policy.rules:
                    if (rule.source_zone.name == zone1_name and 
                        rule.destination_zone.name == zone2_name and
                        rule.action == ActionType.ALLOW):
                        should_block = False
                        break
                
                test_result = {
                    'zones': f"{zone1_name} → {zone2_name}",
                    'source': device1.ip_address,
                    'target': device2.ip_address,
                    'expected_block': should_block,
                    'tests': []
                }
                
                # Тест ping
                try:
                    ping_result = self._ping_test(device1.ip_address, device2.ip_address)
                    
                    test_result['tests'].append({
                        'type': 'ping',
                        'result': ping_result,
                        'expected': not should_block,  # Если должен блокировать, ожидаем False
                        'status': 'passed' if (ping_result != should_block) else 'failed'
                    })
                    
                    if ping_result != should_block:
                        results['passed'] += 1
                    else:
                        results['failed'] += 1
                        
                except Exception as e:
                    test_result['tests'].append({
                        'type': 'ping',
                        'result': False,
                        'error': str(e),
                        'status': 'error'
                    })
                    results['failed'] += 1
                
                # Тест порта 80 (HTTP)
                try:
                    port_result = self._port_test(device1.ip_address, device2.ip_address, 80)
                    
                    test_result['tests'].append({
                        'type': 'tcp_80',
                        'result': port_result,
                        'expected': not should_block,
                        'status': 'passed' if (port_result != should_block) else 'failed'
                    })
                    
                    if port_result != should_block:
                        results['passed'] += 1
                    else:
                        results['failed'] += 1
                        
                except Exception as e:
                    test_result['tests'].append({
                        'type': 'tcp_80',
                        'result': False,
                        'error': str(e),
                        'status': 'error'
                    })
                    results['failed'] += 1
                
                results['tests'].append(test_result)
        
        return results
    
    def test_performance(self, policy: NetworkPolicy) -> Dict:
        """Тест производительности (задержки)"""
        results = {
            'name': 'Тест производительности',
            'description': 'Измерение задержек в сети',
            'tests': [],
            'average_latency': 0,
            'max_latency': 0,
            'min_latency': float('inf'),
        }
        
        latencies = []
        
        # Измеряем задержки внутри зон
        for zone_name, zone in policy.zones.items():
            if len(zone.devices) < 2:
                continue
            
            # Используем ThreadPool для параллельного тестирования
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                
                for i in range(min(3, len(zone.devices))):  # Тестируем до 3 устройств
                    for j in range(i + 1, min(3, len(zone.devices))):
                        device1 = zone.devices[i]
                        device2 = zone.devices[j]
                        
                        future = executor.submit(
                            self._measure_latency,
                            device1.ip_address,
                            device2.ip_address
                        )
                        futures.append((device1.ip_address, device2.ip_address, future))
                
                for source, target, future in futures:
                    try:
                        latency = future.result(timeout=10)
                        
                        if latency is not None:
                            latencies.append(latency)
                            
                            results['tests'].append({
                                'source': source,
                                'target': target,
                                'latency': latency,
                                'zone': zone_name,
                                'status': 'completed'
                            })
                            
                    except Exception as e:
                        results['tests'].append({
                            'source': source,
                            'target': target,
                            'error': str(e),
                            'status': 'error'
                        })
        
        if latencies:
            results['average_latency'] = sum(latencies) / len(latencies)
            results['max_latency'] = max(latencies)
            results['min_latency'] = min(latencies)
        
        return results
    
    def _ping_test(self, source_ip: str, target_ip: str, timeout: int = 2) -> bool:
        """Проверка ping между устройствами"""
        try:
            # Для Windows и Linux/macOS разные команды
            import platform
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            
            result = subprocess.run(
                ['ping', param, '2', '-W', str(timeout), target_ip],
                capture_output=True,
                text=True,
                timeout=timeout + 1
            )
            
            return result.returncode == 0
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _port_test(self, source_ip: str, target_ip: str, port: int, timeout: int = 2) -> bool:
        """Проверка доступности TCP порта"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            # Пытаемся подключиться
            result = sock.connect_ex((target_ip, port))
            sock.close()
            
            return result == 0
            
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False
    
    def _measure_latency(self, source_ip: str, target_ip: str, attempts: int = 3) -> Optional[float]:
        """Измерить задержку между устройствами"""
        import platform
        
        try:
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            
            result = subprocess.run(
                ['ping', param, str(attempts), '-W', '1', target_ip],
                capture_output=True,
                text=True,
                timeout=attempts + 2
            )
            
            # Парсим вывод ping для получения средней задержки
            output = result.stdout
            
            if 'windows' in platform.system().lower():
                # Парсинг для Windows
                import re
                match = re.search(r'Average = (\d+)ms', output)
                if match:
                    return float(match.group(1))
            else:
                # Парсинг для Linux/macOS
                import re
                match = re.search(r'min/avg/max/.+? = [\d.]+/([\d.]+)/', output)
                if match:
                    return float(match.group(1))
            
            return None
            
        except Exception:
            return None
    
    def _generate_summary(self, test_results: Dict) -> Dict:
        """Сгенерировать сводку по результатам тестов"""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        issues = []
        recommendations = []
        
        for test_name, test_data in test_results.items():
            if 'passed' in test_data and 'failed' in test_data:
                total_tests += test_data['passed'] + test_data['failed']
                passed_tests += test_data['passed']
                failed_tests += test_data['failed']
            
            # Анализируем проблемы
            if test_name == 'isolation' and test_data.get('failed', 0) > 0:
                issues.append("Обнаружены утечки трафика между зонами")
                recommendations.append("Проверьте правила брандмауэра между зонами")
            
            if test_name == 'connectivity' and test_data.get('failed', 0) > 0:
                issues.append("Проблемы со связностью внутри зон")
                recommendations.append("Проверьте настройки сети и VLAN")
            
            if test_name == 'performance' and test_data.get('average_latency', 0) > 100:
                issues.append("Высокая задержка в сети")
                recommendations.append("Проверьте качество соединения и нагрузку на сеть")
        
        score = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': f"{score:.1f}%",
            'issues': issues,
            'recommendations': recommendations,
            'overall_status': 'passed' if score >= 90 else 'warning' if score >= 70 else 'failed'
        }
    
    def stop_validation(self):
        """Остановить текущую валидацию"""
        self.is_testing = False
    
    def get_latest_results(self) -> List[Dict]:
        """Получить результаты последней валидации"""
        return self.test_results.copy()
