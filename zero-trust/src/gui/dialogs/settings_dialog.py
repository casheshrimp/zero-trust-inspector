"""
Диалоговое окно настроек приложения
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QLabel, QLineEdit, QComboBox, QCheckBox,
    QSpinBox, QPushButton, QGroupBox, QFormLayout,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from ...core.constants import DEFAULT_SETTINGS

class SettingsDialog(QDialog):
    """Диалог настроек приложения"""
    
    settings_changed = pyqtSignal(dict)  # Сигнал при изменении настроек
    
    def __init__(self, current_settings: dict, parent=None):
        super().__init__(parent)
        self.current_settings = current_settings.copy()
        self.init_ui()
        
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Настройки ZeroTrust Inspector")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        layout = QVBoxLayout(self)
        
        # Вкладки настроек
        tab_widget = QTabWidget()
        
        # Вкладка "Общие"
        general_tab = self.create_general_tab()
        tab_widget.addTab(general_tab, "Общие")
        
        # Вкладка "Сеть"
        network_tab = self.create_network_tab()
        tab_widget.addTab(network_tab, "Сеть")
        
        # Вкладка "Безопасность"
        security_tab = self.create_security_tab()
        tab_widget.addTab(security_tab, "Безопасность")
        
        # Вкладка "Интерфейс"
        interface_tab = self.create_interface_tab()
        tab_widget.addTab(interface_tab, "Интерфейс")
        
        layout.addWidget(tab_widget)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        self.defaults_button = QPushButton("По умолчанию")
        self.defaults_button.clicked.connect(self.restore_defaults)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_settings)
        self.save_button.setDefault(True)
        
        button_layout.addWidget(self.defaults_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
    def create_general_tab(self) -> QWidget:
        """Создать вкладку общих настроек"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Язык интерфейса
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Русский", "English", "Deutsch"])
        lang_index = {"ru": 0, "en": 1, "de": 2}
        current_lang = self.current_settings.get('language', 'ru')
        self.language_combo.setCurrentIndex(lang_index.get(current_lang, 0))
        layout.addRow("Язык интерфейса:", self.language_combo)
        
        # Автосохранение
        self.auto_save_check = QCheckBox("Автоматически сохранять проекты")
        self.auto_save_check.setChecked(self.current_settings.get('auto_save', True))
        layout.addRow(self.auto_save_check)
        
        # Автообновления
        self.auto_update_check = QCheckBox("Проверять обновления при запуске")
        self.auto_update_check.setChecked(self.current_settings.get('check_updates', True))
        layout.addRow(self.auto_update_check)
        
        # Максимальное количество устройств
        self.max_devices_spin = QSpinBox()
        self.max_devices_spin.setRange(10, 1000)
        self.max_devices_spin.setValue(self.current_settings.get('max_devices', 254))
        self.max_devices_spin.setSuffix(" устройств")
        layout.addRow("Максимум устройств:", self.max_devices_spin)
        
        # Размер журнала
        self.log_size_spin = QSpinBox()
        self.log_size_spin.setRange(1, 1000)
        self.log_size_spin.setValue(self.current_settings.get('log_size_mb', 100))
        self.log_size_spin.setSuffix(" МБ")
        layout.addRow("Размер журнала:", self.log_size_spin)
        
        return widget
        
    def create_network_tab(self) -> QWidget:
        """Создать вкладку сетевых настроек"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Диапазон сканирования
        self.network_edit = QLineEdit()
        self.network_edit.setText(self.current_settings.get('scan_network', '192.168.1.0/24'))
        self.network_edit.setPlaceholderText("например: 192.168.1.0/24")
        layout.addRow("Диапазон сканирования:", self.network_edit)
        
        # Скорость сканирования
        self.scan_speed_combo = QComboBox()
        self.scan_speed_combo.addItems(["Медленная", "Нормальная", "Быстрая"])
        speed_map = {"slow": 0, "normal": 1, "fast": 2}
        current_speed = self.current_settings.get('scan_speed', 'normal')
        self.scan_speed_combo.setCurrentIndex(speed_map.get(current_speed, 1))
        layout.addRow("Скорость сканирования:", self.scan_speed_combo)
        
        # Автоклассификация
        self.auto_classify_check = QCheckBox("Автоматически классифицировать устройства")
        self.auto_classify_check.setChecked(self.current_settings.get('auto_classify', True))
        layout.addRow(self.auto_classify_check)
        
        # Таймаут сканирования
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 60)
        self.timeout_spin.setValue(self.current_settings.get('scan_timeout', 10))
        self.timeout_spin.setSuffix(" секунд")
        layout.addRow("Таймаут сканирования:", self.timeout_spin)
        
        # Порты для сканирования
        self.ports_edit = QLineEdit()
        default_ports = "22,80,443,3389,9100"
        self.ports_edit.setText(self.current_settings.get('scan_ports', default_ports))
        self.ports_edit.setPlaceholderText("например: 22,80,443,3389")
        layout.addRow("Порты для сканирования:", self.ports_edit)
        
        return widget
        
    def create_security_tab(self) -> QWidget:
        """Создать вкладку настроек безопасности"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Политика по умолчанию
        self.default_policy_combo = QComboBox()
        self.default_policy_combo.addItems(["Запретить всё", "Разрешить всё", "Спрашивать"])
        policy_map = {"deny": 0, "allow": 1, "ask": 2}
        current_policy = self.current_settings.get('default_policy', 'deny')
        self.default_policy_combo.setCurrentIndex(policy_map.get(current_policy, 0))
        layout.addRow("Политика по умолчанию:", self.default_policy_combo)
        
        # Автоизоляция
        self.auto_isolate_check = QCheckBox("Автоматически изолировать устройства с высоким риском")
        self.auto_isolate_check.setChecked(self.current_settings.get('auto_isolate', True))
        layout.addRow(self.auto_isolate_check)
        
        # Резервное копирование
        self.backup_check = QCheckBox("Создавать резервные копии перед изменением правил")
        self.backup_check.setChecked(self.current_settings.get('enable_backup', True))
        layout.addRow(self.backup_check)
        
        # Логирование
        self.logging_check = QCheckBox("Вести журнал безопасности")
        self.logging_check.setChecked(self.current_settings.get('enable_logging', True))
        layout.addRow(self.logging_check)
        
        # Дней хранения логов
        self.log_retention_spin = QSpinBox()
        self.log_retention_spin.setRange(1, 365)
        self.log_retention_spin.setValue(self.current_settings.get('log_retention_days', 30))
        self.log_retention_spin.setSuffix(" дней")
        layout.addRow("Хранить логи:", self.log_retention_spin)
        
        return widget
        
    def create_interface_tab(self) -> QWidget:
        """Создать вкладку настроек интерфейса"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Тема оформления
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Тёмная", "Светлая", "Системная"])
        theme_map = {"dark": 0, "light": 1, "system": 2}
        current_theme = self.current_settings.get('theme', 'dark')
        self.theme_combo.setCurrentIndex(theme_map.get(current_theme, 0))
        layout.addRow("Тема оформления:", self.theme_combo)
        
        # Размер шрифта
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 20)
        self.font_size_spin.setValue(self.current_settings.get('font_size', 10))
        self.font_size_spin.setSuffix(" pt")
        layout.addRow("Размер шрифта:", self.font_size_spin)
        
        # Показывать иконки
        self.show_icons_check = QCheckBox("Показывать иконки устройств")
        self.show_icons_check.setChecked(self.current_settings.get('show_icons', True))
        layout.addRow(self.show_icons_check)
        
        # Анимации
        self.animations_check = QCheckBox("Включить анимации интерфейса")
        self.animations_check.setChecked(self.current_settings.get('enable_animations', True))
        layout.addRow(self.animations_check)
        
        # Подсказки
        self.tooltips_check = QCheckBox("Показывать всплывающие подсказки")
        self.tooltips_check.setChecked(self.current_settings.get('show_tooltips', True))
        layout.addRow(self.tooltips_check)
        
        return widget
        
    def restore_defaults(self):
        """Восстановить настройки по умолчанию"""
        reply = QMessageBox.question(
            self,
            "Восстановление настроек",
            "Вы уверены, что хотите восстановить настройки по умолчанию?\n"
            "Все текущие настройки будут потеряны.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.current_settings = DEFAULT_SETTINGS.copy()
            
            # Обновляем UI
            self.language_combo.setCurrentIndex(0)
            self.auto_save_check.setChecked(True)
            self.auto_update_check.setChecked(True)
            self.max_devices_spin.setValue(254)
            self.log_size_spin.setValue(100)
            
            self.network_edit.setText("192.168.1.0/24")
            self.scan_speed_combo.setCurrentIndex(1)
            self.auto_classify_check.setChecked(True)
            self.timeout_spin.setValue(10)
            self.ports_edit.setText("22,80,443,3389,9100")
            
            self.default_policy_combo.setCurrentIndex(0)
            self.auto_isolate_check.setChecked(True)
            self.backup_check.setChecked(True)
            self.logging_check.setChecked(True)
            self.log_retention_spin.setValue(30)
            
            self.theme_combo.setCurrentIndex(0)
            self.font_size_spin.setValue(10)
            self.show_icons_check.setChecked(True)
            self.animations_check.setChecked(True)
            self.tooltips_check.setChecked(True)
            
    def save_settings(self):
        """Сохранить настройки"""
        try:
            # Общие
            lang_map = {0: "ru", 1: "en", 2: "de"}
            self.current_settings['language'] = lang_map[self.language_combo.currentIndex()]
            self.current_settings['auto_save'] = self.auto_save_check.isChecked()
            self.current_settings['check_updates'] = self.auto_update_check.isChecked()
            self.current_settings['max_devices'] = self.max_devices_spin.value()
            self.current_settings['log_size_mb'] = self.log_size_spin.value()
            
            # Сеть
            self.current_settings['scan_network'] = self.network_edit.text()
            speed_map = {0: "slow", 1: "normal", 2: "fast"}
            self.current_settings['scan_speed'] = speed_map[self.scan_speed_combo.currentIndex()]
            self.current_settings['auto_classify'] = self.auto_classify_check.isChecked()
            self.current_settings['scan_timeout'] = self.timeout_spin.value()
            self.current_settings['scan_ports'] = self.ports_edit.text()
            
            # Безопасность
            policy_map = {0: "deny", 1: "allow", 2: "ask"}
            self.current_settings['default_policy'] = policy_map[self.default_policy_combo.currentIndex()]
            self.current_settings['auto_isolate'] = self.auto_isolate_check.isChecked()
            self.current_settings['enable_backup'] = self.backup_check.isChecked()
            self.current_settings['enable_logging'] = self.logging_check.isChecked()
            self.current_settings['log_retention_days'] = self.log_retention_spin.value()
            
            # Интерфейс
            theme_map = {0: "dark", 1: "light", 2: "system"}
            self.current_settings['theme'] = theme_map[self.theme_combo.currentIndex()]
            self.current_settings['font_size'] = self.font_size_spin.value()
            self.current_settings['show_icons'] = self.show_icons_check.isChecked()
            self.current_settings['enable_animations'] = self.animations_check.isChecked()
            self.current_settings['show_tooltips'] = self.tooltips_check.isChecked()
            
            # Отправляем сигнал
            self.settings_changed.emit(self.current_settings)
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось сохранить настройки: {str(e)}"
            )
