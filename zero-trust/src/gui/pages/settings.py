"""
Страница настроек приложения
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit,
    QGroupBox, QHBoxLayout, QComboBox, QCheckBox, QLineEdit,
    QSpinBox, QDoubleSpinBox, QSlider, QTabWidget, QFormLayout,
    QFileDialog, QMessageBox, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont, QIntValidator


class SettingsPage(QWidget):
    """Страница настроек приложения"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("ZeroTrust Project", "ZeroTrust Inspector")
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Настройки ZeroTrust Inspector")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)
        
        # Описание
        description = QLabel(
            "Настройте параметры приложения для оптимальной работы."
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Вкладки настроек
        self.tab_widget = QTabWidget()
        
        # Вкладка: Общие настройки
        general_tab = QWidget()
        general_layout = QVBoxLayout()
        
        # Группа: Интерфейс
        ui_group = QGroupBox("Интерфейс")
        ui_layout = QFormLayout()
        
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Темная", "Светлая", "Системная"])
        
        self.combo_language = QComboBox()
        self.combo_language.addItems(["Русский", "English", "Deutsch", "Français"])
        
        self.check_animations = QCheckBox("Включить анимации")
        self.check_animations.setChecked(True)
        
        self.check_system_tray = QCheckBox("Сворачивать в системный трей")
        self.check_system_tray.setChecked(True)
        
        ui_layout.addRow("Тема:", self.combo_theme)
        ui_layout.addRow("Язык:", self.combo_language)
        ui_layout.addRow(self.check_animations)
        ui_layout.addRow(self.check_system_tray)
        
        ui_group.setLayout(ui_layout)
        general_layout.addWidget(ui_group)
        
        # Группа: Уведомления
        notify_group = QGroupBox("Уведомления")
        notify_layout = QFormLayout()
        
        self.check_notify_errors = QCheckBox("Ошибки и предупреждения")
        self.check_notify_errors.setChecked(True)
        
        self.check_notify_scans = QCheckBox("Завершение сканирования")
        self.check_notify_scans.setChecked(True)
        
        self.check_notify_updates = QCheckBox("Доступны обновления")
        self.check_notify_updates.setChecked(True)
        
        self.spin_notify_duration = QSpinBox()
        self.spin_notify_duration.setRange(1, 60)
        self.spin_notify_duration.setSuffix(" сек")
        
        notify_layout.addRow(self.check_notify_errors)
        notify_layout.addRow(self.check_notify_scans)
        notify_layout.addRow(self.check_notify_updates)
        notify_layout.addRow("Длительность уведомлений:", self.spin_notify_duration)
        
        notify_group.setLayout(notify_layout)
        general_layout.addWidget(notify_group)
        
        general_layout.addStretch()
        general_tab.setLayout(general_layout)
        
        # Вкладка: Безопасность
        security_tab = QWidget()
        security_layout = QVBoxLayout()
        
        # Группа: Настройки сканирования
        scan_group = QGroupBox("Настройки сканирования")
        scan_layout = QFormLayout()
        
        self.spin_scan_threads = QSpinBox()
        self.spin_scan_threads.setRange(1, 32)
        self.spin_scan_threads.setValue(4)
        
        self.spin_scan_timeout = QSpinBox()
        self.spin_scan_timeout.setRange(1, 300)
        self.spin_scan_timeout.setValue(30)
        self.spin_scan_timeout.setSuffix(" сек")
        
        self.check_scan_stealth = QCheckBox("Стелс-режим сканирования")
        
        scan_layout.addRow("Количество потоков:", self.spin_scan_threads)
        scan_layout.addRow("Таймаут сканирования:", self.spin_scan_timeout)
        scan_layout.addRow(self.check_scan_stealth)
        
        scan_group.setLayout(scan_layout)
        security_layout.addWidget(scan_group)
        
        # Группа: Шифрование
        crypto_group = QGroupBox("Шифрование")
        crypto_layout = QFormLayout()
        
        self.combo_crypto_strength = QComboBox()
        self.combo_crypto_strength.addItems(["Низкое (128-bit)", "Среднее (256-bit)", "Высокое (512-bit)"])
        
        self.check_encrypt_config = QCheckBox("Шифровать файлы конфигурации")
        self.check_encrypt_config.setChecked(True)
        
        self.check_auto_key_rotation = QCheckBox("Автоматическая ротация ключей")
        
        crypto_layout.addRow("Уровень шифрования:", self.combo_crypto_strength)
        crypto_layout.addRow(self.check_encrypt_config)
        crypto_layout.addRow(self.check_auto_key_rotation)
        
        crypto_group.setLayout(crypto_layout)
        security_layout.addWidget(crypto_group)
        
        security_layout.addStretch()
        security_tab.setLayout(security_layout)
        
        # Вкладка: Хранилище
        storage_tab = QWidget()
        storage_layout = QVBoxLayout()
        
        # Группа: Пути
        paths_group = QGroupBox("Пути хранения данных")
        paths_layout = QFormLayout()
        
        self.edit_config_path = QLineEdit()
        self.edit_config_path.setReadOnly(True)
        self.btn_browse_config = QPushButton("Обзор...")
        
        self.edit_logs_path = QLineEdit()
        self.edit_logs_path.setReadOnly(True)
        self.btn_browse_logs = QPushButton("Обзор...")
        
        self.edit_exports_path = QLineEdit()
        self.edit_exports_path.setReadOnly(True)
        self.btn_browse_exports = QPushButton("Обзор...")
        
        paths_layout.addRow("Конфигурации:", self.create_path_row(self.edit_config_path, self.btn_browse_config))
        paths_layout.addRow("Логи:", self.create_path_row(self.edit_logs_path, self.btn_browse_logs))
        paths_layout.addRow("Экспорт:", self.create_path_row(self.edit_exports_path, self.btn_browse_exports))
        
        paths_group.setLayout(paths_layout)
        storage_layout.addWidget(paths_group)
        
        # Группа: Лимиты
        limits_group = QGroupBox("Лимиты хранилища")
        limits_layout = QFormLayout()
        
        self.spin_max_log_size = QSpinBox()
        self.spin_max_log_size.setRange(10, 10000)
        self.spin_max_log_size.setValue(100)
        self.spin_max_log_size.setSuffix(" МБ")
        
        self.spin_max_backups = QSpinBox()
        self.spin_max_backups.setRange(1, 100)
        self.spin_max_backups.setValue(10)
        
        self.check_auto_cleanup = QCheckBox("Автоматическая очистка старых файлов")
        self.check_auto_cleanup.setChecked(True)
        
        limits_layout.addRow("Максимальный размер логов:", self.spin_max_log_size)
        limits_layout.addRow("Максимальное количество бэкапов:", self.spin_max_backups)
        limits_layout.addRow(self.check_auto_cleanup)
        
        limits_group.setLayout(limits_layout)
        storage_layout.addWidget(limits_group)
        
        storage_layout.addStretch()
        storage_tab.setLayout(storage_layout)
        
        # Добавляем вкладки
        self.tab_widget.addTab(general_tab, "Общие")
        self.tab_widget.addTab(security_tab, "Безопасность")
        self.tab_widget.addTab(storage_tab, "Хранилище")
        
        layout.addWidget(self.tab_widget)
        
        # Кнопки действий
        buttons_layout = QHBoxLayout()
        self.btn_save = QPushButton("Сохранить настройки")
        self.btn_reset = QPushButton("Сбросить к умолчаниям")
        self.btn_apply = QPushButton("Применить")
        
        buttons_layout.addWidget(self.btn_save)
        buttons_layout.addWidget(self.btn_reset)
        buttons_layout.addWidget(self.btn_apply)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Подключение сигналов
        self.btn_save.clicked.connect(self.save_settings)
        self.btn_reset.clicked.connect(self.reset_to_defaults)
        self.btn_apply.clicked.connect(self.apply_settings)
        
        self.btn_browse_config.clicked.connect(lambda: self.browse_directory(self.edit_config_path))
        self.btn_browse_logs.clicked.connect(lambda: self.browse_directory(self.edit_logs_path))
        self.btn_browse_exports.clicked.connect(lambda: self.browse_directory(self.edit_exports_path))
        
    def create_path_row(self, line_edit, button):
        """Создать строку с полем ввода и кнопкой обзора"""
        layout = QHBoxLayout()
        layout.addWidget(line_edit)
        layout.addWidget(button)
        layout.setContentsMargins(0, 0, 0, 0)
        
        widget = QWidget()
        widget.setLayout(layout)
        return widget
        
    def load_settings(self):
        """Загрузить сохраненные настройки"""
        # Интерфейс
        self.combo_theme.setCurrentIndex(self.settings.value("Theme", 0, type=int))
        self.combo_language.setCurrentIndex(self.settings.value("Language", 0, type=int))
        self.check_animations.setChecked(self.settings.value("Animations", True, type=bool))
        self.check_system_tray.setChecked(self.settings.value("SystemTray", True, type=bool))
        
        # Уведомления
        self.check_notify_errors.setChecked(self.settings.value("NotifyErrors", True, type=bool))
        self.check_notify_scans.setChecked(self.settings.value("NotifyScans", True, type=bool))
        self.check_notify_updates.setChecked(self.settings.value("NotifyUpdates", True, type=bool))
        self.spin_notify_duration.setValue(self.settings.value("NotifyDuration", 5, type=int))
        
        # Безопасность
        self.spin_scan_threads.setValue(self.settings.value("ScanThreads", 4, type=int))
        self.spin_scan_timeout.setValue(self.settings.value("ScanTimeout", 30, type=int))
        self.check_scan_stealth.setChecked(self.settings.value("ScanStealth", False, type=bool))
        
        self.combo_crypto_strength.setCurrentIndex(self.settings.value("CryptoStrength", 1, type=int))
        self.check_encrypt_config.setChecked(self.settings.value("EncryptConfig", True, type=bool))
        self.check_auto_key_rotation.setChecked(self.settings.value("AutoKeyRotation", False, type=bool))
        
        # Хранилище
        self.edit_config_path.setText(self.settings.value("ConfigPath", "./configs", type=str))
        self.edit_logs_path.setText(self.settings.value("LogsPath", "./logs", type=str))
        self.edit_exports_path.setText(self.settings.value("ExportsPath", "./exports", type=str))
        
        self.spin_max_log_size.setValue(self.settings.value("MaxLogSize", 100, type=int))
        self.spin_max_backups.setValue(self.settings.value("MaxBackups", 10, type=int))
        self.check_auto_cleanup.setChecked(self.settings.value("AutoCleanup", True, type=bool))
        
    def save_settings(self):
        """Сохранить настройки"""
        self.apply_settings()
        self.settings.sync()
        QMessageBox.information(self, "Сохранено", "Настройки успешно сохранены!")
        
    def apply_settings(self):
        """Применить текущие настройки"""
        # Интерфейс
        self.settings.setValue("Theme", self.combo_theme.currentIndex())
        self.settings.setValue("Language", self.combo_language.currentIndex())
        self.settings.setValue("Animations", self.check_animations.isChecked())
        self.settings.setValue("SystemTray", self.check_system_tray.isChecked())
        
        # Уведомления
        self.settings.setValue("NotifyErrors", self.check_notify_errors.isChecked())
        self.settings.setValue("NotifyScans", self.check_notify_scans.isChecked())
        self.settings.setValue("NotifyUpdates", self.check_notify_updates.isChecked())
        self.settings.setValue("NotifyDuration", self.spin_notify_duration.value())
        
        # Безопасность
        self.settings.setValue("ScanThreads", self.spin_scan_threads.value())
        self.settings.setValue("ScanTimeout", self.spin_scan_timeout.value())
        self.settings.setValue("ScanStealth", self.check_scan_stealth.isChecked())
        
        self.settings.setValue("CryptoStrength", self.combo_crypto_strength.currentIndex())
        self.settings.setValue("EncryptConfig", self.check_encrypt_config.isChecked())
        self.settings.setValue("AutoKeyRotation", self.check_auto_key_rotation.isChecked())
        
        # Хранилище
        self.settings.setValue("ConfigPath", self.edit_config_path.text())
        self.settings.setValue("LogsPath", self.edit_logs_path.text())
        self.settings.setValue("ExportsPath", self.edit_exports_path.text())
        
        self.settings.setValue("MaxLogSize", self.spin_max_log_size.value())
        self.settings.setValue("MaxBackups", self.spin_max_backups.value())
        self.settings.setValue("AutoCleanup", self.check_auto_cleanup.isChecked())
        
    def reset_to_defaults(self):
        """Сбросить настройки к значениям по умолчанию"""
        reply = QMessageBox.question(
            self, "Сброс настроек",
            "Вы уверены, что хотите сбросить все настройки к значениям по умолчанию?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.clear()
            self.load_settings()
            QMessageBox.information(self, "Сброс", "Настройки сброшены к значениям по умолчанию!")
            
    def browse_directory(self, line_edit):
        """Выбрать директорию"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Выберите директорию",
            line_edit.text(),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if dir_path:
            line_edit.setText(dir_path)
