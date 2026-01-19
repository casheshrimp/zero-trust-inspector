"""
Диалоговое окно экспорта конфигурации
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QCheckBox, QGroupBox,
    QPushButton, QFileDialog, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
import os
from pathlib import Path

class ExportDialog(QDialog):
    """Диалог экспорта конфигурации"""
    
    export_requested = pyqtSignal(dict)  # Сигнал с параметрами экспорта
    
    def __init__(self, policy_name: str, platforms: list, parent=None):
        super().__init__(parent)
        self.policy_name = policy_name
        self.platforms = platforms
        self.init_ui()
        
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle(f"Экспорт политики: {self.policy_name}")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Основные параметры
        form_layout = QFormLayout()
        
        # Платформа
        self.platform_combo = QComboBox()
        self.platform_combo.addItems([p['name'] for p in self.platforms])
        form_layout.addRow("Целевая платформа:", self.platform_combo)
        
        # Формат файла
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Текстовый файл (.txt)", "Конфигурация (.conf)", "Скрипт (.sh/.ps1)"])
        form_layout.addRow("Формат файла:", self.format_combo)
        
        # Путь сохранения
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        default_path = str(Path.home() / "Desktop" / f"{self.policy_name}.conf")
        self.path_edit.setText(default_path)
        
        self.browse_button = QPushButton("Обзор...")
        self.browse_button.clicked.connect(self.browse_path)
        
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_button)
        form_layout.addRow("Путь сохранения:", path_layout)
        
        layout.addLayout(form_layout)
        
        # Дополнительные опции
        options_group = QGroupBox("Дополнительные опции")
        options_layout = QVBoxLayout(options_group)
        
        self.add_comments_check = QCheckBox("Добавить комментарии в конфигурацию")
        self.add_comments_check.setChecked(True)
        options_layout.addWidget(self.add_comments_check)
        
        self.create_backup_check = QCheckBox("Создать резервную копию существующего файла")
        self.create_backup_check.setChecked(True)
        options_layout.addWidget(self.create_backup_check)
        
        self.validate_config_check = QCheckBox("Проверить конфигурацию перед сохранением")
        self.validate_config_check.setChecked(True)
        options_layout.addWidget(self.validate_config_check)
        
        self.open_after_check = QCheckBox("Открыть файл после экспорта")
        self.open_after_check.setChecked(True)
        options_layout.addWidget(self.open_after_check)
        
        layout.addWidget(options_group)
        
        # Предпросмотр (заглушка)
        preview_group = QGroupBox("Предпросмотр")
        preview_layout = QVBoxLayout(preview_group)
        preview_label = QLabel("Предпросмотр будет доступен после выбора платформы")
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_label.setStyleSheet("color: gray; font-style: italic;")
        preview_layout.addWidget(preview_label)
        
        self.show_preview_button = QPushButton("Показать предпросмотр")
        self.show_preview_button.clicked.connect(self.show_preview)
        preview_layout.addWidget(self.show_preview_button)
        
        layout.addWidget(preview_group)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        
        self.export_button = QPushButton("Экспортировать")
        self.export_button.clicked.connect(self.start_export)
        self.export_button.setDefault(True)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.export_button)
        
        layout.addLayout(button_layout)
        
    def browse_path(self):
        """Выбрать путь сохранения"""
        file_filter = "Конфигурационные файлы (*.conf *.txt *.sh *.ps1);;Все файлы (*.*)"
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить конфигурацию",
            self.path_edit.text(),
            file_filter
        )
        
        if filename:
            self.path_edit.setText(filename)
            
    def show_preview(self):
        """Показать предпросмотр конфигурации"""
        platform_index = self.platform_combo.currentIndex()
        if platform_index < 0 or platform_index >= len(self.platforms):
            return
            
        platform = self.platforms[platform_index]
        
        # Здесь будет вызов генератора конфигурации
        # preview_text = self.generate_preview(platform['id'])
        
        QMessageBox.information(
            self,
            "Предпросмотр",
            f"Предпросмотр конфигурации для {platform['name']}\n\n"
            "Эта функция будет реализована в следующей версии."
        )
        
    def start_export(self):
        """Начать экспорт"""
        try:
            # Проверка пути
            export_path = self.path_edit.text().strip()
            if not export_path:
                raise ValueError("Не указан путь сохранения")
            
            # Проверка расширения
            if not any(export_path.endswith(ext) for ext in ['.txt', '.conf', '.sh', '.ps1']):
                export_path += '.conf'
                self.path_edit.setText(export_path)
            
            # Проверка существования файла
            if os.path.exists(export_path) and self.create_backup_check.isChecked():
                reply = QMessageBox.question(
                    self,
                    "Файл существует",
                    f"Файл {os.path.basename(export_path)} уже существует.\n"
                    "Создать резервную копию и перезаписать?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            # Подготавливаем параметры экспорта
            platform_index = self.platform_combo.currentIndex()
            if platform_index < 0:
                raise ValueError("Не выбрана платформа")
            
            platform = self.platforms[platform_index]
            
            export_params = {
                'platform': platform['id'],
                'platform_name': platform['name'],
                'file_path': export_path,
                'format': self.format_combo.currentText(),
                'options': {
                    'add_comments': self.add_comments_check.isChecked(),
                    'create_backup': self.create_backup_check.isChecked(),
                    'validate_config': self.validate_config_check.isChecked(),
                    'open_after': self.open_after_check.isChecked(),
                }
            }
            
            # Отправляем сигнал
            self.export_requested.emit(export_params)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось начать экспорт: {str(e)}"
            )
