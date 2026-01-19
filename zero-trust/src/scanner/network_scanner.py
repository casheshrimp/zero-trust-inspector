"""
Модуль сканирования сети
"""

import ipaddress
import socket
import threading
import time
from typing import List, Dict, Optional, Set
from queue import Queue
import nmap
import netifaces
from scapy.all import ARP, Ether, srp
from scapy.layers.l2 import getmacbyip

from ..core.models import NetworkDevice, DeviceType
from .device_classifier import DeviceClassifier
from .oui_database import OUILookup

class NetworkScanner:
    """Сканер сети"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.nm = nmap.PortScanner()
        self.oui_lookup = OUILookup()
        self.classifier = DeviceClassifier()
        self.scan_results = []
        self.is_scanning = False
        
    def get_local_interfaces(self) -> List[Dict]:
        """Получить список локальных сетевых интерфейсов"""
        interfaces = []
        
        try:
            for iface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(iface)
                
                if netifaces.AF_INET in addrs:
                    for addr_info in addrs[netifaces.AF_INET]:
                        ip = addr_info.get('addr')
                        netmask = addr_info.get('netmask')
                        
                        if ip and netmask and not ip.startswith('127.'):
                            try:
                                # Вычисляем сеть
                                network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
                                
                                interfaces.append({
                                    'interface': iface,
                                    'ip': ip,
                                    'netmask': netmask,
                                    'network': str(network),
                                    'gateway': self._get_gateway(iface)
                                })
                            except ValueError as e:
                                if self.logger:
                                    self.logger.warning(f"Ошибка обработки интерфейса {iface}: {e}")
                elif self.logger:
                    self.logger.debug(f"Интерфейс {iface} не имеет IPv4 адреса")
                    
        except Exception as e:
            if self.logger:
                self.logger.error(f"Ошибка при получении интерфейсов: {e}")
        
        return interfaces
    
    def _get_gateway(self, interface: str) -> Optional[str]:
        """Получить шлюз по умолчанию для интерфейса"""
        try:
            gateways = netifaces.gateways()
            default_gateway = gateways.get('default', {})
            
            # Ищем шлюз для данного интерфейса
            for family, gateway_info in default_gateway.items():
                if family == netifaces.AF_INET:
                    gw_ip, gw_iface = gateway_info[:2]
                    if gw_iface == interface:
                        return gw_ip
        except Exception:
            pass
        
        return None
    
    def arp_scan(self, network: str, timeout: int = 2) -> List[Dict]:
        """Выполнить ARP-сканирование сети"""
        devices = []
        
        try:
            # Создаем ARP-пакет
            arp = ARP(pdst=network)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether/arp
            
            # Отправляем пакет
            result = srp(packet, timeout=timeout, verbose=0)[0]
            
            for sent, received in result:
                ip = received.psrc
                mac = received.hwsrc
                
                # Получаем вендора по OUI
                vendor = self.oui_lookup.get_vendor(mac)
                
                # Пытаемся получить hostname
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except (socket.herror, socket.gaierror):
                    hostname = None
                
                devices.append({
                    'ip': ip,
                    'mac': mac,
                    'vendor': vendor,
                    'hostname': hostname
                })
                
                if self.logger:
                    self.logger.debug(f"Найдено устройство: {ip} ({mac}) - {vendor}")
                    
        except Exception as e:
            if self.logger:
                self.logger.error(f"Ошибка при ARP-сканировании: {e}")
        
        return devices
    
    def port_scan(self, ip: str, ports: List[int] = None) -> Dict:
        """Сканировать порты устройства"""
        if ports is None:
            ports = [22, 23, 80, 443, 8080, 3389, 5353, 9100, 1900]
        
        try:
            # Используем nmap для сканирования портов
            self.nm.scan(ip, arguments=f"-p {','.join(map(str, ports))} -T4")
            
            if ip in self.nm.all_hosts():
                host_info = self.nm[ip]
                
                # Получаем открытые порты
                open_ports = []
                for proto in host_info.all_protocols():
                    for port in host_info[proto]:
                        if host_info[proto][port]['state'] == 'open':
                            open_ports.append(port)
                
                # Пытаемся определить OS
                os_info = None
                if 'osmatch' in host_info:
                    os_matches = host_info['osmatch']
                    if os_matches:
                        os_info = os_matches[0].get('name', 'Unknown')
                
                return {
                    'open_ports': open_ports,
                    'os_info': os_info,
                    'hostname': host_info.hostname(),
                    'status': host_info.state()
                }
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Ошибка при сканировании портов {ip}: {e}")
        
        return {'open_ports': [], 'os_info': None, 'hostname': None, 'status': 'down'}
    
    def classify_device(self, arp_info: Dict, port_info: Dict) -> NetworkDevice:
        """Классифицировать устройство"""
        # Получаем тип устройства от классификатора
        device_type = self.classifier.classify(
            arp_info['vendor'],
            port_info['open_ports'],
            port_info['os_info']
        )
        
        # Создаем объект устройства
        device = NetworkDevice(
            ip_address=arp_info['ip'],
            mac_address=arp_info['mac'],
            hostname=port_info.get('hostname') or arp_info.get('hostname'),
            device_type=device_type,
            vendor=arp_info['vendor'],
            open_ports=port_info['open_ports'],
            os_info=port_info['os_info'],
            risk_score=self.classifier.calculate_risk_score(device_type, port_info['open_ports'])
        )
        
        return device
    
    def scan_network(self, network: str, callback=None) -> List[NetworkDevice]:
        """Полное сканирование сети"""
        self.is_scanning = True
        devices = []
        
        if self.logger:
            self.logger.info(f"Начато сканирование сети: {network}")
        
        # Этап 1: ARP-сканирование
        if self.logger:
            self.logger.info("Этап 1: ARP-сканирование...")
        
        arp_devices = self.arp_scan(network)
        
        if callback:
            callback("ARP сканирование завершено", len(arp_devices))
        
        # Этап 2: Сканирование портов и классификация
        if self.logger:
            self.logger.info("Этап 2: Сканирование портов и классификация...")
        
        for i, arp_info in enumerate(arp_devices):
            if not self.is_scanning:
                break
            
            ip = arp_info['ip']
            
            if self.logger:
                self.logger.debug(f"Сканирование устройства {ip} ({i+1}/{len(arp_devices)})")
            
            # Сканируем порты
            port_info = self.port_scan(ip)
            
            # Классифицируем устройство
            device = self.classify_device(arp_info, port_info)
            devices.append(device)
            
            if callback:
                callback(f"Обработано устройство: {ip}", i+1, len(arp_devices))
        
        self.is_scanning = False
        
        if self.logger:
            self.logger.info(f"Сканирование завершено. Найдено устройств: {len(devices)}")
        
        return devices
    
    def stop_scan(self):
        """Остановить сканирование"""
        self.is_scanning = False
        if self.logger:
            self.logger.info("Сканирование остановлено по запросу пользователя")
    
    def quick_scan(self) -> List[NetworkDevice]:
        """Быстрое сканирование (тестовые данные)"""
        test_devices = [
            NetworkDevice(
                ip_address="192.168.1.1",
                mac_address="00:11:22:33:44:55",
                hostname="router",
                device_type=DeviceType.ROUTER,
                vendor="TP-Link",
                open_ports=[80, 443],
                risk_score=0.3
            ),
            NetworkDevice(
                ip_address="192.168.1.10",
                mac_address="AA:BB:CC:DD:EE:FF",
                hostname="home-pc",
                device_type=DeviceType.COMPUTER,
                vendor="Dell",
                open_ports=[80, 443, 3389],
                risk_score=0.2
            ),
            NetworkDevice(
                ip_address="192.168.1.20",
                mac_address="11:22:33:44:55:66",
                hostname="android-phone",
                device_type=DeviceType.PHONE,
                vendor="Samsung",
                open_ports=[],
                risk_score=0.4
            ),
            NetworkDevice(
                ip_address="192.168.1.30",
                mac_address="FF:EE:DD:CC:BB:AA",
                hostname="smart-tv",
                device_type=DeviceType.TV,
                vendor="Sony",
                open_ports=[80, 1900],
                risk_score=0.6
            ),
            NetworkDevice(
                ip_address="192.168.1.40",
                mac_address="22:33:44:55:66:77",
                hostname="hp-printer",
                device_type=DeviceType.PRINTER,
                vendor="HP",
                open_ports=[80, 9100],
                risk_score=0.5
            ),
            NetworkDevice(
                ip_address="192.168.1.50",
                mac_address="33:44:55:66:77:88",
                hostname="security-camera",
                device_type=DeviceType.CAMERA,
                vendor="Xiaomi",
                open_ports=[80, 554],
                risk_score=0.7
            ),
        ]
        
        if self.logger:
            self.logger.info(f"Быстрое сканирование: создано {len(test_devices)} тестовых устройств")
        
        return test_devices
