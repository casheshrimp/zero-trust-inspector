"""
Страница генератора правил
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit,
    QGroupBox, QHBoxLayout
)
from PyQt6.QtCore import Qt


class GeneratorPage(QWidget):
    """Страница генератора правил безопасности"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Генератор правил Zero-Trust")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)
        
        # Описание
        description = QLabel(
            "Здесь вы можете автоматически сгенерировать правила безопасности "
            "на основе выбранных устройств и политик."
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Группа настроек генерации
        settings_group = QGroupBox("Настройки генерации")
        settings_layout = QVBoxLayout()
        
        # Кнопки выбора типа правил
        buttons_layout = QHBoxLayout()
        self.btn_firewall = QPushButton("Правила фаервола")
        self.btn_access = QPushButton("Правила доступа")
        self.btn_monitoring = QPushButton("Правила мониторинга")
        
        buttons_layout.addWidget(self.btn_firewall)
        buttons_layout.addWidget(self.btn_access)
        buttons_layout.addWidget(self.btn_monitoring)
        settings_layout.addLayout(buttons_layout)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Поле вывода правил
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setPlaceholderText(
            "Здесь будут отображаться сгенерированные правила..."
        )
        layout.addWidget(self.text_output)
        
        # Кнопки действий
        actions_layout = QHBoxLayout()
        self.btn_generate = QPushButton("Сгенерировать правила")
        self.btn_clear = QPushButton("Очистить")
        self.btn_export = QPushButton("Экспортировать")
        
        actions_layout.addWidget(self.btn_generate)
        actions_layout.addWidget(self.btn_clear)
        actions_layout.addWidget(self.btn_export)
        layout.addLayout(actions_layout)
        
        self.setLayout(layout)
