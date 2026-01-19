import sys

def check_dependencies():
    dependencies = [
        ("PyQt6", "PyQt6"),
        ("python-nmap", "nmap"),
        ("scapy", "scapy"),
        ("Jinja2", "jinja2"),
        ("psutil", "psutil"),
        ("netifaces", "netifaces"),
        ("PyYAML", "yaml"),
    ]
    
    print("Проверка зависимостей ZeroTrust Inspector...")
    
    all_ok = True
    for package_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✓ {package_name} установлен")
        except ImportError:
            print(f"✗ {package_name} НЕ установлен")
            all_ok = False

    if all_ok:
        print("✅ Все зависимости установлены успешно!")
        return 0
    else:
        print("❌ Некоторые зависимости отсутствуют")
        print("Установите их командой: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(check_dependencies())
