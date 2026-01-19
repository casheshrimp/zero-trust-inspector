"""
Страница отчетов
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit,
    QGroupBox, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QDateEdit, QCheckBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont


class ReportsPage(QWidget):
    """Страница отчетов и аналитики"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Отчеты Zero-Trust")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)
        
        # Описание
        description = QLabel(
            "Просмотр и генерация отчетов о состоянии безопасности вашей сети."
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Панель фильтров
        filters_group = QGroupBox("Фильтры отчетов")
        filters_layout = QVBoxLayout()
        
        # Первая строка фильтров
        filters_row1 = QHBoxLayout()
        self.combo_report_type = QComboBox()
        self.combo_report_type.addItems([
            "Общий отчет безопасности",
            "Отчет по устройствам", 
            "Отчет по правилам",
            "Отчет по инцидентам",
            "Аудит изменений"
        ])
        
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-7))
        self.date_from.setCalendarPopup(True)
        
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        
        filters_row1.addWidget(QLabel("Тип отчета:"))
        filters_row1.addWidget(self.combo_report_type)
        filters_row1.addWidget(QLabel("С:"))
        filters_row1.addWidget(self.date_from)
        filters_row1.addWidget(QLabel("По:"))
        filters_row1.addWidget(self.date_to)
        filters_row1.addStretch()
        
        # Вторая строка фильтров
        filters_row2 = QHBoxLayout()
        self.check_include_graphs = QCheckBox("Включить графики")
        self.check_include_graphs.setChecked(True)
        
        self.check_export_pdf = QCheckBox("Подготовить для PDF")
        self.check_export_pdf.setChecked(False)
        
        filters_row2.addWidget(self.check_include_graphs)
        filters_row2.addWidget(self.check_export_pdf)
        filters_row2.addStretch()
        
        filters_layout.addLayout(filters_row1)
        filters_layout.addLayout(filters_row2)
        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)
        
        # Кнопки действий
        buttons_layout = QHBoxLayout()
        self.btn_generate = QPushButton("Сгенерировать отчет")
        self.btn_refresh = QPushButton("Обновить данные")
        self.btn_export = QPushButton("Экспортировать")
        self.btn_print = QPushButton("Печать")
        
        buttons_layout.addWidget(self.btn_generate)
        buttons_layout.addWidget(self.btn_refresh)
        buttons_layout.addWidget(self.btn_export)
        buttons_layout.addWidget(self.btn_print)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        # Таблица отчетов
        self.table_reports = QTableWidget()
        self.table_reports.setColumnCount(6)
        self.table_reports.setHorizontalHeaderLabels([
            "Дата", "Тип отчета", "Статус", "Устройств", "Правил", "Рекомендации"
        ])
        self.table_reports.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_reports.setAlternatingRowColors(True)
        
        layout.addWidget(self.table_reports)
        
        # Область детального просмотра
        detail_group = QGroupBox("Детали отчета")
        detail_layout = QVBoxLayout()
        
        self.text_report_detail = QTextEdit()
        self.text_report_detail.setReadOnly(True)
        self.text_report_detail.setPlaceholderText("Выберите отчет для просмотра деталей...")
        
        detail_layout.addWidget(self.text_report_detail)
        detail_group.setLayout(detail_layout)
        layout.addWidget(detail_group)
        
        # Статистика
        stats_layout = QHBoxLayout()
        self.label_total_reports = QLabel("Всего отчетов: 0")
        self.label_last_report = QLabel("Последний отчет: -")
        self.label_coverage = QLabel("Покрытие: 0%")
        
        for label in [self.label_total_reports, self.label_last_report, self.label_coverage]:
            stats_layout.addWidget(label)
            
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        self.setLayout(layout)
        
        # Подключение сигналов
        self.btn_generate.clicked.connect(self.generate_report)
        self.btn_refresh.clicked.connect(self.refresh_data)
        self.table_reports.itemSelectionChanged.connect(self.show_report_detail)
        
        # Инициализация тестовых данных
        self.refresh_data()
        
    def generate_report(self):
        """Сгенерировать новый отчет"""
        report_type = self.combo_report_type.currentText()
        date_from = self.date_from.date().toString("dd.MM.yyyy")
        date_to = self.date_to.date().toString("dd.MM.yyyy")
        
        # Добавление тестовой записи в таблицу
        row = self.table_reports.rowCount()
        self.table_reports.insertRow(row)
        
        current_date = QDate.currentDate().toString("dd.MM.yyyy")
        self.table_reports.setItem(row, 0, QTableWidgetItem(current_date))
        self.table_reports.setItem(row, 1, QTableWidgetItem(report_type))
        self.table_reports.setItem(row, 2, QTableWidgetItem("✅ Завершен"))
        self.table_reports.setItem(row, 3, QTableWidgetItem("15"))
        self.table_reports.setItem(row, 4, QTableWidgetItem("42"))
        self.table_reports.setItem(row, 5, QTableWidgetItem("Все правила проверены"))
        
        # Обновление статистики
        self.update_statistics()
        
        # Показать детали отчета
        self.show_sample_report(report_type)
        
    def refresh_data(self):
        """Обновить данные таблицы"""
        self.table_reports.setRowCount(0)
        
        # Тестовые данные
        test_data = [
            ["16.01.2026", "Общий отчет безопасности", "✅ Завершен", "12", "38", "3 рекомендации"],
            ["15.01.2026", "Отчет по устройствам", "✅ Завершен", "8", "24", "Добавить 2 устройства"],
            ["14.01.2026", "Аудит изменений", "⚠ Частично", "15", "42", "Проверить изменения"],
            ["13.01.2026", "Отчет по инцидентам", "✅ Завершен", "10", "31", "1 инцидент решен"],
        ]
        
        for data in test_data:
            row = self.table_reports.rowCount()
            self.table_reports.insertRow(row)
            for col, value in enumerate(data):
                self.table_reports.setItem(row, col, QTableWidgetItem(value))
                
        self.update_statistics()
        
    def update_statistics(self):
        """Обновить статистику"""
        total = self.table_reports.rowCount()
        self.label_total_reports.setText(f"Всего отчетов: {total}")
        
        if total > 0:
            last_date = self.table_reports.item(total-1, 0).text()
            self.label_last_report.setText(f"Последний отчет: {last_date}")
            
        # Простое вычисление покрытия (пример)
        coverage = min(total * 25, 100)
        self.label_coverage.setText(f"Покрытие: {coverage}%")
        
    def show_report_detail(self):
        """Показать детали выбранного отчета"""
        selected = self.table_reports.selectedItems()
        if not selected:
            return
            
        row = selected[0].row()
        report_type = self.table_reports.item(row, 1).text()
        self.show_sample_report(report_type)
        
    def show_sample_report(self, report_type):
        """Показать пример отчета"""
        report_content = f"""
        <div style='font-family: "Segoe UI", Arial, sans-serif;'>
            <h1 style='color: #0B5394;'>Отчет: {report_type}</h1>
            <h2>Дата генерации: {QDate.currentDate().toString("dd.MM.yyyy")}</h2>
            
            <div style='background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0;'>
                <h3>📊 Общая статистика</h3>
                <ul>
                    <li>Всего устройств в сети: <strong>15</strong></li>
                    <li>Всего правил безопасности: <strong>42</strong></li>
                    <li>Уровень соответствия Zero-Trust: <strong style='color: #93C47D;'>85%</strong></li>
                    <li>Последняя проверка: <strong>Сегодня, 02:34</strong></li>
                </ul>
            </div>
            
            <div style='background-color: #fff8e1; padding: 15px; border-radius: 5px; margin: 10px 0;'>
                <h3>⚠️ Обнаруженные проблемы</h3>
                <ol>
                    <li>2 устройства без шифрования трафика</li>
                    <li>1 правило с избыточными привилегиями</li>
                    <li>Устройство IoT имеет доступ к серверной зоне</li>
                </ol>
            </div>
            
            <div style='background-color: #e8f5e9; padding: 15px; border-radius: 5px; margin: 10px 0;'>
                <h3>✅ Рекомендации</h3>
                <ol>
                    <li>Добавить шифрование для устройств IoT</li>
                    <li>Обновить правила доступа для гостевой сети</li>
                    <li>Включить многофакторную аутентификацию для администраторов</li>
                </ol>
            </div>
            
            <div style='margin-top: 20px; padding-top: 15px; border-top: 1px solid #ddd;'>
                <p><strong>Сгенерировано системой ZeroTrust Inspector v1.0.0</strong></p>
                <p style='color: #666; font-size: 12px;'>
                    Данный отчет является автоматически сгенерированным документом.<br>
                    Для получения дополнительной информации обратитесь к администратору безопасности.
                </p>
            </div>
        </div>
        """
        
        self.text_report_detail.setHtml(report_content)
