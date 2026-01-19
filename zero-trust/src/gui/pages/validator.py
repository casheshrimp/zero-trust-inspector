"""
Страница валидатора правил
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit,
    QGroupBox, QHBoxLayout, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer


class ValidatorPage(QWidget):
    """Страница валидации правил безопасности"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Валидатор правил Zero-Trust")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)
        
        # Описание
        description = QLabel(
            "Проверьте ваши правила безопасности на соответствие "
            "принципам Zero-Trust архитектуры."
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Область ввода правил
        input_group = QGroupBox("Введите правила для проверки")
        input_layout = QVBoxLayout()
        
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "Вставьте сюда ваши правила (JSON, YAML или текст)...\n\n"
            "Пример:\n"
            "{\n"
            '  "rules": [\n'
            '    {"source": "192.168.1.100", "destination": "internet", "protocol": "tcp", "port": 443},\n'
            '    {"source": "iot_zone", "destination": "server_zone", "protocol": "udp", "port": 5353}\n'
            "  ]\n"
            "}"
        )
        input_layout.addWidget(self.text_input)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Кнопки действий
        buttons_layout = QHBoxLayout()
        self.btn_validate = QPushButton("Начать проверку")
        self.btn_clear = QPushButton("Очистить")
        self.btn_load_file = QPushButton("Загрузить из файла")
        
        buttons_layout.addWidget(self.btn_validate)
        buttons_layout.addWidget(self.btn_clear)
        buttons_layout.addWidget(self.btn_load_file)
        layout.addLayout(buttons_layout)
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Область результатов
        result_group = QGroupBox("Результаты проверки")
        result_layout = QVBoxLayout()
        
        self.text_result = QTextEdit()
        self.text_result.setReadOnly(True)
        self.text_result.setPlaceholderText("Результаты проверки появятся здесь...")
        result_layout.addWidget(self.text_result)
        
        # Статус проверки
        self.status_label = QLabel("Готов к проверке")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_layout.addWidget(self.status_label)
        
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        # Статистика
        stats_layout = QHBoxLayout()
        self.label_total = QLabel("Всего правил: 0")
        self.label_valid = QLabel("Валидных: 0")
        self.label_invalid = QLabel("Невалидных: 0")
        self.label_warnings = QLabel("Предупреждений: 0")
        
        for label in [self.label_total, self.label_valid, self.label_invalid, self.label_warnings]:
            stats_layout.addWidget(label)
            
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        self.setLayout(layout)
        
        # Подключение сигналов
        self.btn_validate.clicked.connect(self.start_validation)
        self.btn_clear.clicked.connect(self.clear_all)
        
    def start_validation(self):
        """Начать процесс валидации"""
        rules_text = self.text_input.toPlainText().strip()
        if not rules_text:
            self.show_result("Ошибка", "Введите правила для проверки!", "error")
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Проверка начата...")
        
        # Имитация процесса проверки
        for i in range(101):
            QTimer.singleShot(i * 20, lambda val=i: self.update_progress(val))
            
    def update_progress(self, value):
        """Обновить прогресс-бар"""
        self.progress_bar.setValue(value)
        if value == 100:
            self.show_result("Успех", "Проверка завершена! Все правила соответствуют Zero-Trust.", "success")
            self.progress_bar.setVisible(False)
            
    def show_result(self, title, message, result_type):
        """Показать результат проверки"""
        colors = {
            "success": "#93C47D",
            "error": "#E06666", 
            "warning": "#FFD966",
            "info": "#76A5AF"
        }
        
        color = colors.get(result_type, "#76A5AF")
        html = f"""
        <div style='padding: 10px; border-radius: 5px; background-color: {color}20; border-left: 4px solid {color};'>
            <h3 style='margin: 0; color: {color};'>{title}</h3>
            <p>{message}</p>
        </div>
        """
        self.text_result.setHtml(html)
        self.status_label.setText(f"Проверка завершена: {title}")
        
    def clear_all(self):
        """Очистить все поля"""
        self.text_input.clear()
        self.text_result.clear()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Готов к проверке")
