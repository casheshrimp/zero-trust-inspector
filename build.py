#!/usr/bin/env python3
"""
Скрипт сборки ZeroTrust Inspector
"""

import os
import sys
import shutil
from pathlib import Path
import subprocess

def build_exe():
    """Собрать исполняемый файл с помощью PyInstaller"""
    print("🔨 Сборка ZeroTrust Inspector...")
    
    # Создаем spec файл для PyInstaller
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('configs', 'configs'),
        ('src/gui/styles', 'src/gui/styles'),
    ],
    hiddenimports=[
        'PyQt6',
        'nmap',
        'jinja2',
        'scapy',
        'psutil',
        'netifaces',
        'yaml',
        'colorlog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ZeroTrustInspector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Запуск без консоли
    icon='assets/icons/app.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    
    # Создаем spec файл
    spec_path = Path("ZeroTrustInspector.spec")
    spec_path.write_text(spec_content, encoding='utf-8')
    
    try:
        # Запускаем PyInstaller
        result = subprocess.run(
            ['pyinstaller', '--clean', '--noconfirm', str(spec_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Сборка завершена успешно!")
            print(f"📁 Исполняемый файл: dist/ZeroTrustInspector")
        else:
            print("❌ Ошибка сборки:")
            print(result.stderr)
            
    except FileNotFoundError:
        print("❌ PyInstaller не установлен. Установите его:")
        print("pip install pyinstaller")
        return False
    
    return True

def create_installer():
    """Создать установщик (для Windows)"""
    print("📦 Создание установщика...")
    
    # Создаем структуру для установщика
    installer_dir = Path("installer")
    installer_dir.mkdir(exist_ok=True)
    
    # Копируем файлы
    files_to_copy = [
        "dist/ZeroTrustInspector",
        "README.md",
        "LICENSE",
        "configs/default.yaml"
    ]
    
    for file_path in files_to_copy:
        if Path(file_path).exists():
            shutil.copy2(file_path, installer_dir)
    
    print(f"📁 Установщик создан в: {installer_dir}")

def clean_build():
    """Очистить файлы сборки"""
    print("🧹 Очистка файлов сборки...")
    
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['ZeroTrustInspector.spec']
    
    for dir_name in dirs_to_remove:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"Удалена папка: {dir_name}")
    
    for file_name in files_to_remove:
        if Path(file_name).exists():
            Path(file_name).unlink()
            print(f"Удален файл: {file_name}")

def main():
    """Главная функция сборки"""
    print("=" * 50)
    print("ZeroTrust Inspector - Сборка приложения")
    print("=" * 50)
    
    # Проверяем зависимости
    try:
        import PyInstaller
    except ImportError:
        print("⚠️  PyInstaller не установлен")
        print("Установите: pip install pyinstaller")
        return
    
    # Меню сборки
    print("\nВыберите действие:")
    print("1. Собрать исполняемый файл")
    print("2. Создать установщик")
    print("3. Очистить файлы сборки")
    print("4. Выход")
    
    choice = input("\nВаш выбор (1-4): ").strip()
    
    if choice == '1':
        build_exe()
    elif choice == '2':
        create_installer()
    elif choice == '3':
        clean_build()
    elif choice == '4':
        print("👋 Выход")
    else:
        print("❌ Неверный выбор")

if __name__ == "__main__":
    main()
