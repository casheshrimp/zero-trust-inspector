"""
Страница "Обзор сети" (Dashboard)
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QProgressBar,
    QGroupBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt

class DashboardPage(QWidget):
    """Страница дашборда"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Заголовок
        header = QLabel("Обзор сети")
        header.setObjectName("TitleLabel")
        layout.addWidget(header)
        
        # Карточки статистики
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        # Карточка: Всего устройств
        total_card = self.create_stat_card("Всего устройств", "14", "● ● ● ● ● ● ● ● ● ● ● ● ● ●", "#0B5394")
        stats_layout.addWidget(total_card)
        
        # Карточка: Онлайн
        online_card = self.create_stat_card("Онлайн", "12", "● ● ● ● ● ● ● ● ● ● ● ●", "#93C47D")
        stats_layout.addWidget(online_card)
        
        # Карточка: Оффлайн
        offline_card = self.create_stat_card("Оффлайн", "2", "● ●", "#E06666")
        stats_layout.addWidget(offline_card)
        
        layout.addLayout(stats_layout)
        
        # Прогресс уровня защиты
        protection_frame = QFrame()
        protection_frame.setObjectName("Card")
        protection_layout = QVBoxLayout(protection_frame)
        
        protection_label = QLabel("Уровень защиты")
        protection_label.setObjectName("HeadingLabel")
        protection_layout.addWidget(protection_label)
        
        self.protection_bar = QProgressBar()
        self.protection_bar.setValue(67)
        self.protection_bar.setFormat("███▒▒ 67%")
        self.protection_bar.setStyleSheet("""
            QProgressBar {
                height: 24px;
                font-weight: bold;
            }
        """)
        protection_layout.addWidget(self.protection_bar)
        
        protection_info = QLabel("Последнее сканирование: 15 минут назад | Последняя проверка: 2 часа назад")
        protection_info.setStyleSheet("color: #B0B0B0; font-size: 12px;")
        protection_layout.addWidget(protection_info)
        
        layout.addWidget(protection_frame)
        
        # Зоны безопасности
        zones_group = QGroupBox("Зоны безопасности")
        zones_group.setObjectName("Card")
        zones_layout = QHBoxLayout(zones_group)
        zones_layout.setSpacing(20)
        
        # Зона: Доверенные
        trusted_zone = self.create_zone_card("✅ ДОВЕРЕННЫЕ", "5 устройств", [
            "💻 Ноутбук Маши", "📱 iPhone Маши", "💻 Ноутбук Паши",
            "🖨️ Принтер", "💻 Сервер"
        ], "#90EE90")
        zones_layout.addWidget(trusted_zone)
        
        # Зона: Умный дом
        iot_zone = self.create_zone_card("⚠️ УМНЫЙ ДОМ", "6 устройств", [
            "💡 Умная лампа", "📷 Камера", "📺 Умный телевизор",
            "🔌 Умная розетка", "🌡️ Датчик температуры", "🔊 Умная колонка"
        ], "#FFFF99")
        zones_layout.addWidget(iot_zone)
        
        # Зона: Гости
        guest_zone = self.create_zone_card("👥 ГОСТИ", "3 устройства", [
            "📱 Гостевой телефон", "💻 Гостевой ноутбук", "📱 Планшет"
        ], "#D3D3D3")
        zones_layout.addWidget(guest_zone)
        
        layout.addWidget(zones_group)
        
        # Последние действия
        actions_frame = QFrame()
        actions_frame.setObjectName("Card")
        actions_layout = QVBoxLayout(actions_frame)
        
        actions_label = QLabel("Последние действия")
        actions_label.setObjectName("HeadingLabel")
        actions_layout.addWidget(actions_label)
        
        actions = [
            ("✅", "14:30 - Сканирование завершено (12 устройств)"),
            ("⚠️", "14:15 - Обнаружено новое устройство"),
            ("✅", "13:45 - Правила применены успешно"),
            ("✅", "12:30 - Валидация пройдена (95%)"),
            ("🔍", "12:00 - Запущено сканирование портов"),
        ]
        
        for icon, text in actions:
            action_widget = QLabel(f"{icon} {text}")
            action_widget.setStyleSheet("padding: 6px 0; border-bottom: 1px solid #404040;")
            actions_layout.addWidget(action_widget)
        
        layout.addWidget(actions_frame)
        
        # Кнопки быстрых действий
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        quick_scan_btn = QPushButton("🔄 Быстрое сканирование")
        quick_scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #0B5394;
                font-size: 14px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #3D85C6;
            }
        """)
        
        check_security_btn = QPushButton("✅ Проверить безопасность")
        check_security_btn.setStyleSheet("""
            QPushButton {
                background-color: #93C47D;
                font-size: 14px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #A8D197;
            }
        """)
        
        buttons_layout.addWidget(quick_scan_btn)
        buttons_layout.addWidget(check_security_btn)
        buttons_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        layout.addLayout(buttons_layout)
        
        # Пространство внизу
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
    
    def create_stat_card(self, title, value, dots, color):
        """Создать карточку статистики"""
        frame = QFrame()
        frame.setObjectName("Card")
        frame.setStyleSheet(f"border-left: 4px solid {color};")
        
        layout = QVBoxLayout(frame)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #B0B0B0; font-size: 12px;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 28px; font-weight: bold; margin: 5px 0;")
        layout.addWidget(value_label)
        
        dots_label = QLabel(dots)
        dots_label.setStyleSheet("font-size: 16px; color: #505050;")
        layout.addWidget(dots_label)
        
        return frame
    
    def create_zone_card(self, title, subtitle, devices, color):
        """Создать карточку зоны"""
        frame = QFrame()
        frame.setObjectName("ZoneCard")
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color}20;
                border: 2px solid {color};
                border-radius: 8px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        
        # Заголовок зоны
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        layout.addWidget(title_label)
        
        # Подзаголовок
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("font-size: 12px; color: #666666; margin-bottom: 10px;")
        layout.addWidget(subtitle_label)
        
        # Устройства
        for device in devices:
            device_label = QLabel(f"    {device}")
            device_label.setStyleSheet("padding: 4px 0;")
            layout.addWidget(device_label)
        
        # Пространство
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        return frame
