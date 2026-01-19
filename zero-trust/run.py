#!/usr/bin/env python3
"""
Альтернативный запуск ZeroTrust Inspector
"""

import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def check_and_install():
    """Проверить и установить зависимости"""
    print("🔍 Проверка зависимостей...")
    
    try:
        import PyQt6
        print("✅ PyQt6 установлен")
    except ImportError:
        print("❌ PyQt6 не установлен")
        print("Установка PyQt6...")
        os.system("pip install PyQt6")
    
    try:
        import nmap
        print("✅ python-nmap установлен")
    except ImportError:
        print("❌ python-nmap не установлен")
        print("Установка python-nmap...")
        os.system("pip install python-nmap")
    
    try:
        import scapy
        print("✅ scapy установлен")
    except ImportError:
        print("❌ scapy не установлен")
        print("Установка scapy...")
        os.system("pip install scapy")
    
    print("\n" + "="*50)
    print("       ZERO TRUST INSPECTOR v1.0.0")
    print("="*50 + "\n")

def main():
    """Главная функция запуска"""
    check_and_install()
    
    # Создаем необходимые директории
    directories = [
        "logs", "configs", "exports", "backups",
        "assets", "assets/icons", "configs/templates"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"📁 Создана папка: {dir_path}")
    
    # Запускаем приложение
    try:
        from main import main as app_main
        sys.exit(app_main())
    except Exception as e:
        print(f"\n❌ Ошибка запуска: {e}")
        print("\nПопробуйте выполнить:")
        print("1. pip install -r requirements.txt")
        print("2. python main.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())