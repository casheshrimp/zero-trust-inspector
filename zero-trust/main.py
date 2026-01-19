#!/usr/bin/env python3
"""
ZeroTrust Inspector - Главный файл приложения
Полнофункциональная версия с реальным сканированием и GUI
"""

import sys
import logging
import traceback
from pathlib import Path

# Настройка логирования
def setup_logging():
    """Настройка системы логирования"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Создаем логгер
    logger = logging.getLogger("ZeroTrustInspector")
    logger.setLevel(logging.DEBUG)
    
    # Обработчик для файла
    file_handler = logging.FileHandler(
        log_dir / 'zerotrust.log',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Форматирование
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

def check_dependencies():
    """Проверка необходимых зависимостей"""
    dependencies = [
        ("PyQt6", "PyQt6"),
        ("python-nmap", "nmap"),
        ("scapy", "scapy"),
        # ("netifaces", "netifaces"),  # Убираем проверку netifaces
        ("psutil", "psutil"),
    ]
    
    missing = []
    for name, module in dependencies:
        try:
            __import__(module)
            logger.info(f"✓ {name} установлен")
        except ImportError:
            logger.error(f"✗ {name} не установлен")
            missing.append(name)
    
    if missing:
        print(f"\n❌ Отсутствуют зависимости: {', '.join(missing)}")
        print("Установите их командой:")
        print(f"pip install {' '.join(missing)}")
        return False
    return True

def create_directories():
    """Создание необходимых директорий"""
    directories = [
        "logs",
        "configs",
        "exports",
        "backups",
        "assets",
        "assets/icons",
        "assets/styles",
        "configs/templates"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Создана директория: {dir_path}")

def handle_exception(exc_type, exc_value, exc_traceback):
    """Обработчик неперехваченных исключений"""
    logger.critical("Неперехваченное исключение:", 
                   exc_info=(exc_type, exc_value, exc_traceback))
    
    # Показываем сообщение об ошибке
    try:
        from PyQt6.QtWidgets import QMessageBox, QApplication
        app = QApplication.instance()
        if app:
            error_msg = f"""
            ⚠️ КРИТИЧЕСКАЯ ОШИБКА
            
            Тип: {exc_type.__name__}
            Сообщение: {str(exc_value)}
            
            Приложение будет закрыто.
            Подробности в файле logs/zerotrust.log
            """
            QMessageBox.critical(None, "Ошибка", error_msg)
    except:
        pass
    
    sys.exit(1)

def main():
    """Главная функция"""
    sys.excepthook = handle_exception
    
    print("\n" + "="*60)
    print("       ZERO TRUST INSPECTOR v1.0.0")
    print("   Визуализатор и валидатор Zero-Trust политик")
    print("="*60 + "\n")
    
    logger.info("Запуск ZeroTrust Inspector")
    
    # Проверка зависимостей
    if not check_dependencies():
        return 1
    
    # Создание директорий
    create_directories()
    
    # Запуск GUI
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QIcon
        from src.gui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        app.setApplicationName("ZeroTrust Inspector")
        app.setApplicationVersion("1.0.0")
        
        # Загрузка иконки
        try:
            app.setWindowIcon(QIcon("assets/icons/app.png"))
        except:
            pass
        
        # Создание главного окна
        logger.info("Создание главного окна...")
        window = MainWindow()
        window.show()
        
        logger.info("Приложение запущено успешно")
        print("\n✅ Приложение запущено успешно!")
        print("👆 Используйте интерфейс для сканирования сети и создания правил\n")
        
        return app.exec()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске GUI: {e}")
        logger.error(traceback.format_exc())
        print(f"\n❌ Ошибка запуска: {e}")
        print("Проверьте файл logs/zerotrust.log для подробностей")
        return 1

if __name__ == "__main__":
    sys.exit(main())