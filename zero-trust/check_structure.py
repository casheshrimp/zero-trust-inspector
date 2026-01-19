#!/usr/bin/env python3
"""
Проверка структуры проекта ZeroTrust Inspector
"""

import sys
import os
from pathlib import Path

def check_project_structure():
    """Проверить структуру проекта"""
    print("🔍 Проверка структуры проекта ZeroTrust Inspector...")
    print("=" * 50)
    
    # Основные файлы
    required_files = [
        "main.py",
        "run_app.py",
        "requirements.txt",
        "README.md",
        "LICENSE",
        "setup.py",
    ]
    
    # Директории и файлы внутри них
    required_dirs = [
        "src/__init__.py",
        "src/core/__init__.py",
        "src/core/models.py",
        "src/core/exceptions.py",
        "src/core/constants.py",
        "src/gui/__init__.py",
        "src/gui/main_window.py",
        "src/scanner/__init__.py",
        "src/scanner/network_scanner.py",
        "src/policy/__init__.py",
        "src/policy/generator.py",
        "logs/",
        "configs/",
        "configs/templates/",
        "exports/",
        "backups/",
        "assets/",
        "assets/icons/",
    ]
    
    all_ok = True
    
    print("\n📁 Проверка основных файлов:")
    for file in required_files:
        file_path = Path(file)
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✓ {file} ({size} байт)")
        else:
            print(f"  ✗ {file} - ОТСУТСТВУЕТ!")
            all_ok = False
    
    print("\n📁 Проверка структуры папок:")
    for item in required_dirs:
        item_path = Path(item)
        if item.endswith('/'):
            # Это папка
            if item_path.exists():
                print(f"  ✓ Папка {item}")
            else:
                print(f"  ✗ Папка {item} - ОТСУТСТВУЕТ!")
                all_ok = False
        else:
            # Это файл
            if item_path.exists():
                size = item_path.stat().st_size if item_path.exists() else 0
                print(f"  ✓ Файл {item} ({size} байт)")
            else:
                print(f"  ✗ Файл {item} - ОТСУТСТВУЕТ!")
                all_ok = False
    
    # Проверка шаблонов конфигураций
    print("\n🎨 Проверка шаблонов конфигураций:")
    templates = ["openwrt.j2", "windows_firewall.j2", "iptables.j2"]
    for template in templates:
        template_path = Path(f"configs/templates/{template}")
        if template_path.exists():
            print(f"  ✓ Шаблон {template}")
        else:
            print(f"  ⚠ Шаблон {template} отсутствует (можно создать позже)")
    
    # Проверка Python модулей
    print("\n🐍 Проверка Python модулей:")
    try:
        import src.core.models
        print("  ✓ Модуль src.core.models")
    except ImportError as e:
        print(f"  ✗ Ошибка импорта src.core.models: {e}")
        all_ok = False
    
    try:
        import src.gui.main_window
        print("  ✓ Модуль src.gui.main_window")
    except ImportError as e:
        print(f"  ✗ Ошибка импорта src.gui.main_window: {e}")
        all_ok = False
    
    if all_ok:
        print("\n" + "=" * 50)
        print("✅ Структура проекта в порядке!")
        print("\n📋 Инструкция по запуску:")
        print("1. Установите зависимости: pip install -r requirements.txt")
        print("2. Проверьте структуру: python check_structure.py")
        print("3. Запустите приложение: python run_app.py")
        print("4. Или используйте: python main.py")
        print("\n💡 Для разработки установите dev-зависимости:")
        print("   pip install pytest black flake8 mypy")
        return 0
    else:
        print("\n" + "=" * 50)
        print("❌ Обнаружены проблемы со структурой проекта!")
        print("\n🛠 Исправьте следующие проблемы:")
        print("1. Создайте отсутствующие файлы и папки")
        print("2. Проверьте структуру согласно документации")
        print("3. Установите все зависимости")
        return 1

if __name__ == "__main__":
    sys.exit(check_project_structure())
