"""
Диалоговое окно редактирования правил
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QLineEdit, QSpinBox, QCheckBox,
    QTextEdit, QPushButton, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from ...core.models import Rule, ActionType, SecurityZone

class RuleEditorDialog(QDialog):
    """Диалог редактирования правил"""
    
    rule_saved = pyqtSignal(Rule)  # Сигнал при сохранении правила
    
    def __init__(self, zones: dict, rule: Rule = None, parent=None):
        super().__init__(parent)
        self.zones = zones
        self.rule = rule
        self.init_ui()
        
    def init_ui(self):
        """Инициализация интерфейса"""
        title = "Редактирование правила" if self.rule else "Новое правило"
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Основные настройки
        form_layout = QFormLayout()
        
        # Источник
        self.source_combo = QComboBox()
        self.source_combo.addItems(list(self.zones.keys()))
        form_layout.addRow("Источник (зона):", self.source_combo)
        
        # Назначение
        self.dest_combo = QComboBox()
        self.dest_combo.addItems(list(self.zones.keys()))
        form_layout.addRow("Назначение (зона):", self.dest_combo)
        
        # Действие
        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "Разрешить (ALLOW)",
            "Запретить (DENY)",
            "Отклонить (REJECT)",
            "Логировать (LOG)"
        ])
        form_layout.addRow("Действие:", self.action_combo)
        
        layout.addLayout(form_layout)
        
        # Дополнительные параметры
        advanced_group = QGroupBox("Дополнительные параметры")
        advanced_layout = QFormLayout(advanced_group)
        
        # Протокол
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["Любой", "TCP", "UDP", "ICMP"])
        advanced_layout.addRow("Протокол:", self.protocol_combo)
        
        # Порт
        port_layout = QHBoxLayout()
        self.port_check = QCheckBox("Порт:")
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setEnabled(False)
        
        self.port_check.toggled.connect(self.port_spin.setEnabled)
        
        port_layout.addWidget(self.port_check)
        port_layout.addWidget(self.port_spin)
        port_layout.addStretch()
        advanced_layout.addRow("", port_layout)
        
        # Направление
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["Входящий", "Исходящий", "В обе стороны"])
        advanced_layout.addRow("Направление:", self.direction_combo)
        
        layout.addWidget(advanced_group)
        
        # Описание
        layout.addWidget(QLabel("Описание:"))
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        layout.addWidget(self.description_edit)
        
        # Включено
        self.enabled_check = QCheckBox("Правило активно")
        self.enabled_check.setChecked(True)
        layout.addWidget(self.enabled_check)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_rule)
        self.save_button.setDefault(True)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        # Заполняем значения, если редактируем существующее правило
        if self.rule:
            self.load_rule_data()
            
    def load_rule_data(self):
        """Загрузить данные правила в форму"""
        if not self.rule:
            return
            
        # Зоны
        source_index = self.source_combo.findText(self.rule.source_zone.name)
        if source_index >= 0:
            self.source_combo.setCurrentIndex(source_index)
            
        dest_index = self.dest_combo.findText(self.rule.destination_zone.name)
        if dest_index >= 0:
            self.dest_combo.setCurrentIndex(dest_index)
        
        # Действие
        action_map = {
            ActionType.ALLOW: 0,
            ActionType.DENY: 1,
            ActionType.REJECT: 2,
            ActionType.LOG: 3
        }
        self.action_combo.setCurrentIndex(action_map.get(self.rule.action, 1))
        
        # Протокол
        protocol_map = {"any": 0, "tcp": 1, "udp": 2, "icmp": 3}
        self.protocol_combo.setCurrentIndex(protocol_map.get(self.rule.protocol, 0))
        
        # Порт
        if self.rule.port:
            self.port_check.setChecked(True)
            self.port_spin.setValue(self.rule.port)
        
        # Описание
        self.description_edit.setText(self.rule.description)
        
        # Включено
        self.enabled_check.setChecked(self.rule.enabled)
        
    def save_rule(self):
        """Сохранить правило"""
        try:
            # Проверка данных
            source_zone_name = self.source_combo.currentText()
            dest_zone_name = self.dest_combo.currentText()
            
            if not source_zone_name or not dest_zone_name:
                raise ValueError("Необходимо выбрать зоны")
            
            if source_zone_name == dest_zone_name:
                reply = QMessageBox.question(
                    self,
                    "Правило внутри зоны",
                    "Вы создаёте правило для трафика внутри одной зоны.\n"
                    "Это нормально для разрешения внутреннего трафика.\n"
                    "Продолжить?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            # Получаем объекты зон
            source_zone = self.zones.get(source_zone_name)
            dest_zone = self.zones.get(dest_zone_name)
            
            if not source_zone or not dest_zone:
                raise ValueError("Одна из зон не найдена")
            
            # Действие
            action_map = {
                0: ActionType.ALLOW,
                1: ActionType.DENY,
                2: ActionType.REJECT,
                3: ActionType.LOG
            }
            action = action_map.get(self.action_combo.currentIndex(), ActionType.DENY)
            
            # Протокол
            protocol_map = {0: "any", 1: "tcp", 2: "udp", 3: "icmp"}
            protocol = protocol_map.get(self.protocol_combo.currentIndex(), "any")
            
            # Порт
            port = self.port_spin.value() if self.port_check.isChecked() else None
            
            # Описание
            description = self.description_edit.toPlainText().strip()
            
            # Создаем или обновляем правило
            if self.rule:
                self.rule.source_zone = source_zone
                self.rule.destination_zone = dest_zone
                self.rule.action = action
                self.rule.protocol = protocol
                self.rule.port = port
                self.rule.description = description
                self.rule.enabled = self.enabled_check.isChecked()
            else:
                self.rule = Rule(
                    source_zone=source_zone,
                    destination_zone=dest_zone,
                    action=action,
                    protocol=protocol,
                    port=port,
                    description=description,
                    enabled=self.enabled_check.isChecked()
                )
            
            # Отправляем сигнал
            self.rule_saved.emit(self.rule)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось сохранить правило: {str(e)}"
            )
