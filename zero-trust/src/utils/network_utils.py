"""
Утилиты для работы с сетью
"""

import socket
import ipaddress
import subprocess
from typing import Optional, List
import re

from ..core.exceptions import NetworkError

def is_valid_ip(ip: str) -> bool:
    """Проверить валидность IP-адреса"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def is_valid_mac(mac: str) -> bool:
    """Проверить валидность MAC-адреса"""
    mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
    return bool(mac_pattern.match(mac))

def get_local_ip() -> Optional[str]:
    """Получить локальный IP-адрес"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None

def get_network_interfaces() -> List[Dict]:
    """Получить список сетевых интерфейсов"""
    import netifaces
    
    interfaces = []
    for interface in netifaces.interfaces():
        if interface.startswith('lo'):
            continue
            
        addrs = netifaces.ifaddresses(interface)
        
        if netifaces.AF_INET in addrs:
            ip_info = addrs[netifaces.AF_INET][0]
            
            interfaces.append({
                'name': interface,
                'ip': ip_info['addr'],
                'netmask': ip_info.get('netmask', '255.255.255.0'),
                'status': 'up' if ip_info.get('addr') else 'down'
            })
    
    return interfaces

def ping_host(host: str, timeout: int = 1) -> bool:
    """Проверить доступность хоста"""
    try:
        import platform
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        
        result = subprocess.run(
            ['ping', param, '1', '-W', str(timeout), host],
            capture_output=True,
            text=True,
            timeout=timeout + 1
        )
        
        return result.returncode == 0
        
    except Exception:
        return False

def port_scan_single(host: str, port: int, timeout: int = 2) -> bool:
    """Проверить доступность одного порта"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def get_hostname(ip: str) -> Optional[str]:
    """Получить hostname по IP-адресу"""
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except (socket.herror, socket.gaierror):
        return None

def calculate_subnet(ip: str, netmask: str) -> str:
    """Рассчитать подсеть в формате CIDR"""
    try:
        network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
        return str(network)
    except Exception:
        return f"{ip}/24"
