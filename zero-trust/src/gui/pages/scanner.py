"""
Страница "Сканер сети" - обнаружение и классификация устройств
"""

import threading
import time
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QProgressBar,
    QGroupBox, QTableWidget, QTableWidgetItem,
    QTextEdit, QComboBox, QLineEdit, QCheckBox,
    QSplitter, QHeaderView, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont

class ScannerPage(QWidget):
    """Страница сканирования сети"""
    
    scan_completed = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.scanning = False
        self.scan_progress = 0
        self.devices = []
        self.init_ui()
        self.setup_connections()
        
        # Тестовые данные для демонстрации
        self.demo_devices = [
            {
                "ip": "192.168.1.1",
                "mac": "AA:BB:CC:DD:EE:FF",
                "hostname": "Router-AC68U",
                "vendor": "ASUS",
                "type": "router",
                "ports": [80, 443, 22, 53],
                "status": "online",
                "risk": "low",
                "icon": "🌐"
            },
            {
                "ip": "192.168.1.100",
                "mac": "00:11:22:33:44:55",
                "hostname": "Ноутбук Маши",
                "vendor": "Apple",
                "type": "computer",
                "ports": [22, 445, 3389, 5900],
                "status": "online",
                "risk": "low",
                "icon": "💻"
            },
            {
                "ip": "192.168.1.150",
                "mac": "AA:BB:CC:11:22:33",
                "hostname": "Умная лампа",
                "vendor": "Philips Hue",
                "type": "iot",
                "ports": [80],
                "status": "online",
                "risk": "medium",
                "icon": "💡"
            },
            {
                "ip": "192.168.1.200",
                "mac": "08:00:27:AB:CD:EF",
                "hostname": "Принтер",
                "vendor": "HP",
                "type": "printer",
                "ports": [9100, 631],
                "status": "online",
                "risk": "low",
                "icon": "🖨️"
            },
        ]
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Заголовок и кнопки управления
        header_layout = QHBoxLayout()
        
        title = QLabel("🔍 Сканер сети")
        title.setObjectName("TitleLabel")
        header_layout.addWidget(title)
        
        layout.addStretch()
        
        self.start_btn = QPushButton("▶ Запуск")
        self.start_btn.setObjectName("primaryButton")
        self.start_btn.clicked.connect(self.start_scan)
        
        self.stop_btn = QPushButton("⏹️ Остановить")
        self.stop_btn.setObjectName("dangerButton")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_scan)
        
        self.settings_btn = QPushButton("⚙️ Настройки")
        self.settings_btn.clicked.connect(self.show_settings)
        
        header_layout.addWidget(self.start_btn)
        header_layout.addWidget(self.stop_btn)
        header_layout.addWidget(self.settings_btn)
        
        layout.addLayout(header_layout)
        
        # Настройки сканирования
        settings_frame = QFrame()
        settings_frame.setObjectName("Card")
        settings_layout = QHBoxLayout(settings_frame)
        
        settings_layout.addWidget(QLabel("Диапазон:"))
        self.range_combo = QComboBox()
        self.range_combo.addItems(["192.168.1.0/24", "192.168.0.0/24", "10.0.0.0/24", "Вручную..."])
        settings_layout.addWidget(self.range_combo)
        
        settings_layout.addWidget(QLabel("Скорость:"))
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["Быстрая", "Нормальная", "Медленная", "Стелс"])
        self.speed_combo.setCurrentIndex(1)
        settings_layout.addWidget(self.speed_combo)
        
        settings_layout.addWidget(QLabel("Порты:"))
        self.ports_combo = QComboBox()
        self.ports_combo.addItems(["Основные (100)", "Все (1000)", "Избранные", "Кастомные"])
        settings_layout.addWidget(self.ports_combo)
        
        self.deep_scan_cb = QCheckBox("Глубокое сканирование")
        settings_layout.addWidget(self.deep_scan_cb)
        
        settings_layout.addStretch()
        
        layout.addWidget(settings_frame)
        
        # Прогресс сканирования
        self.progress_frame = QFrame()
        self.progress_frame.setObjectName("Card")
        self.progress_frame.setVisible(False)
        progress_layout = QVBoxLayout(self.progress_frame)
        
        self.progress_label = QLabel("Подготовка к сканированию...")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                height: 24px;
                border-radius: 12px;
            }
            QProgressBar::chunk {
                border-radius: 12px;
                background-color: #0B5394;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.time_label = QLabel("Осталось: ~1 мин 20 сек")
        self.time_label.setStyleSheet("color: #B0B0B0; font-size: 11pt;")
        progress_layout.addWidget(self.time_label)
        
        layout.addWidget(self.progress_frame)
        
        # Основная область
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель: список устройств
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        devices_label = QLabel("Обнаруженные устройства")
        devices_label.setObjectName("HeadingLabel")
        left_layout.addWidget(devices_label)
        
        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(6)
        self.devices_table.setHorizontalHeaderLabels(["IP", "MAC", "Тип", "Статус", "Риск", "Действия"])
        self.devices_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.devices_table.verticalHeader().setVisible(False)
        self.devices_table.setAlternatingRowColors(True)
        left_layout.addWidget(self.devices_table)
        
        main_splitter.addWidget(left_panel)
        
        # Правая панель: детали и статистика
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Детали устройства
        details_group = QGroupBox("Детали устройства")
        details_group.setObjectName("Card")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(200)
        details_layout.addWidget(self.details_text)
        
        right_layout.addWidget(details_group)
        
        # Статистика
        stats_group = QGroupBox("Статистика сканирования")
        stats_group.setObjectName("Card")
        stats_layout = QGridLayout(stats_group)
        
        self.stats_labels = {}
        stats_data = [
            ("Найдено:", "0/254", "total"),
            ("Классифицировано:", "0", "classified"),
            ("Неизвестно:", "0", "unknown"),
            ("Время:", "0 сек", "time"),
            ("Открытых портов:", "0", "ports"),
            ("Средний риск:", "Низкий", "risk"),
        ]
        
        for i, (label, value, key) in enumerate(stats_data):
            stats_layout.addWidget(QLabel(label), i // 2, (i % 2) * 2)
            value_label = QLabel(value)
            value_label.setObjectName("InfoLabel")
            stats_layout.addWidget(value_label, i // 2, (i % 2) * 2 + 1)
            self.stats_labels[key] = value_label
        
        right_layout.addWidget(stats_group)
        
        # Кнопки действий
        actions_frame = QFrame()
        actions_layout = QHBoxLayout(actions_frame)
        
        self.classify_btn = QPushButton("🏷️ Классифицировать")
        self.classify_btn.clicked.connect(self.classify_devices)
        
        self.export_btn = QPushButton("📤 Экспорт CSV")
        self.export_btn.clicked.connect(self.export_results)
        
        self.rescan_btn = QPushButton("🔄 Пересканировать")
        self.rescan_btn.clicked.connect(self.rescan_selected)
        
        actions_layout.addWidget(self.classify_btn)
        actions_layout.addWidget(self.export_btn)
        actions_layout.addWidget(self.rescan_btn)
        actions_layout.addStretch()
        
        right_layout.addWidget(actions_frame)
        right_layout.addStretch()
        
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([600, 400])
        
        layout.addWidget(main_splitter, 1)
        
        # Кнопки управления сканированием
        control_layout = QHBoxLayout()
        
        self.pause_btn = QPushButton("⏸️ Пауза")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.toggle_pause)
        
        self.quick_scan_btn = QPushButton("⚡ Быстрое сканирование")
        self.quick_scan_btn.clicked.connect(self.quick_scan)
        
        self.full_scan_btn = QPushButton("🔍 Полное сканирование")
        self.full_scan_btn.clicked.connect(self.full_scan)
        
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.quick_scan_btn)
        control_layout.addWidget(self.full_scan_btn)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
    
    def setup_connections(self):
        """Настройка сигналов"""
        self.devices_table.itemSelectionChanged.connect(self.on_device_selected)
        self.scan_completed.connect(self.on_scan_completed)
    
    def start_scan(self):
        """Начать сканирование"""
        if self.scanning:
            return
        
        self.scanning = True
        self.scan_progress = 0
        self.devices = []
        self.devices_table.setRowCount(0)
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.pause_btn.setEnabled(True)
        self.progress_frame.setVisible(True)
        
        # Запуск сканирования в отдельном потоке
        scan_thread = threading.Thread(target=self.scan_thread, daemon=True)
        scan_thread.start()
        
        # Таймер для обновления прогресса
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self.update_progress)
        self.scan_timer.start(100)
    
    def scan_thread(self):
        """Поток сканирования (имитация)"""
        # Этап 1: ARP сканирование
        self.update_progress_text("ARP сканирование...", 10)
        time.sleep(1.5)
        
        # Этап 2: Ping сканирование
        self.update_progress_text("Ping сканирование...", 30)
        time.sleep(2)
        
        # Этап 3: Сканирование портов
        self.update_progress_text("Сканирование портов...", 60)
        time.sleep(3)
        
        # Этап 4: Идентификация устройств
        self.update_progress_text("Идентификация устройств...", 80)
        time.sleep(1.5)
        
        # Завершение
        self.update_progress_text("Завершение сканирования...", 95)
        time.sleep(0.5)
        
        # Имитация найденных устройств
        self.devices = self.demo_devices.copy()
        self.scan_completed.emit(self.devices)
        
        self.scanning = False
        self.scan_progress = 100
    
    def update_progress_text(self, text, progress):
        """Обновить текст прогресса"""
        self.scan_progress = progress
        # Используем QTimer для обновления UI из другого потока
        QTimer.singleShot(0, lambda: self.progress_label.setText(text))
    
    def update_progress(self):
        """Обновить прогресс-бар"""
        if self.scanning and self.scan_progress < 100:
            self.scan_progress = min(self.scan_progress + 1, 100)
        
        self.progress_bar.setValue(self.scan_progress)
        
        # Обновление времени
        remaining = 120 * (100 - self.scan_progress) / 100
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        self.time_label.setText(f"Осталось: ~{minutes} мин {seconds} сек")
        
        if self.scan_progress >= 100:
            self.scan_timer.stop()
            self.on_scan_completed(self.devices)
    
    def on_scan_completed(self, devices):
        """Обработка завершения сканирования"""
        self.scanning = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.progress_label.setText("Сканирование завершено")
        
        # Обновление таблицы
        self.devices_table.setRowCount(len(devices))
        
        for i, device in enumerate(devices):
            # IP
            ip_item = QTableWidgetItem(device["ip"])
            self.devices_table.setItem(i, 0, ip_item)
            
            # MAC
            mac_item = QTableWidgetItem(device["mac"])
            self.devices_table.setItem(i, 1, mac_item)
            
            # Тип
            type_item = QTableWidgetItem(f"{device['icon']} {device['type']}")
            self.devices_table.setItem(i, 2, type_item)
            
            # Статус
            status_item = QTableWidgetItem(device["status"])
            if device["status"] == "online":
                status_item.setForeground(QColor("#93C47D"))
            else:
                status_item.setForeground(QColor("#E06666"))
            self.devices_table.setItem(i, 3, status_item)
            
            # Риск
            risk_item = QTableWidgetItem(device["risk"])
            if device["risk"] == "low":
                risk_item.setForeground(QColor("#93C47D"))
            elif device["risk"] == "medium":
                risk_item.setForeground(QColor("#FFD966"))
            else:
                risk_item.setForeground(QColor("#E06666"))
            self.devices_table.setItem(i, 4, risk_item)
            
            # Действия
            actions_btn = QPushButton("📋")
            actions_btn.setFixedSize(30, 30)
            actions_btn.clicked.connect(lambda checked, d=device: self.show_device_actions(d))
            self.devices_table.setCellWidget(i, 5, actions_btn)
        
        # Обновление статистики
        self.stats_labels["total"].setText(f"{len(devices)}/254")
        self.stats_labels["classified"].setText(str(len([d for d in devices if d["type"] != "unknown"])))
        self.stats_labels["unknown"].setText(str(len([d for d in devices if d["type"] == "unknown"])))
        self.stats_labels["time"].setText("45 сек")
        
        total_ports = sum(len(d["ports"]) for d in devices)
        self.stats_labels["ports"].setText(str(total_ports))
        
        # Определение среднего риска
        risks = {"low": 0, "medium": 1, "high": 2}
        avg_risk = sum(risks[d["risk"]] for d in devices) / len(devices) if devices else 0
        risk_text = "Низкий" if avg_risk < 0.5 else "Средний" if avg_risk < 1.5 else "Высокий"
        self.stats_labels["risk"].setText(risk_text)
    
    def on_device_selected(self):
        """Обработка выбора устройства"""
        selected_rows = self.devices_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        if row < len(self.devices):
            device = self.devices[row]
            
            details = f"""
            <h3>{device['icon']} {device['hostname']}</h3>
            <hr>
            <b>IP адрес:</b> {device['ip']}<br>
            <b>MAC адрес:</b> {device['mac']}<br>
            <b>Производитель:</b> {device['vendor']}<br>
            <b>Тип устройства:</b> {device['type']}<br>
            <b>Статус:</b> <span style="color:{'#93C47D' if device['status'] == 'online' else '#E06666'}">{device['status']}</span><br>
            <b>Уровень риска:</b> <span style="color:{'#93C47D' if device['risk'] == 'low' else '#FFD966' if device['risk'] == 'medium' else '#E06666'}">{device['risk']}</span><br>
            <br>
            <b>Открытые порты:</b> {', '.join(map(str, device['ports']))}<br>
            <b>Обнаружено:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            """
            
            self.details_text.setHtml(details)
    
    def stop_scan(self):
        """Остановить сканирование"""
        self.scanning = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.progress_label.setText("Сканирование остановлено")
    
    def toggle_pause(self):
        """Приостановить/возобновить сканирование"""
        if self.pause_btn.text() == "⏸️ Пауза":
            self.pause_btn.setText("▶ Возобновить")
            self.progress_label.setText("Сканирование приостановлено")
        else:
            self.pause_btn.setText("⏸️ Пауза")
            self.progress_label.setText("Сканирование возобновлено...")
    
    def quick_scan(self):
        """Быстрое сканирование"""
        self.range_combo.setCurrentText("192.168.1.0/24")
        self.speed_combo.setCurrentText("Быстрая")
        self.ports_combo.setCurrentText("Основные (100)")
        self.deep_scan_cb.setChecked(False)
        self.start_scan()
    
    def full_scan(self):
        """Полное сканирование"""
        self.range_combo.setCurrentText("192.168.1.0/24")
        self.speed_combo.setCurrentText("Нормальная")
        self.ports_combo.setCurrentText("Все (1000)")
        self.deep_scan_cb.setChecked(True)
        self.start_scan()
    
    def classify_devices(self):
        """Классифицировать устройства"""
        QMessageBox.information(self, "Классификация", 
            f"Устройства классифицированы!\n\n"
            f"Всего: {len(self.devices)}\n"
            f"Классифицировано: {len([d for d in self.devices if d['type'] != 'unknown'])}\n"
            f"Неизвестно: {len([d for d in self.devices if d['type'] == 'unknown'])}")
    
    def export_results(self):
        """Экспортировать результаты"""
        from PyQt6.QtWidgets import QFileDialog
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Экспорт результатов", "scan_results.csv", "CSV Files (*.csv)"
        )
        
        if filepath:
            QMessageBox.information(self, "Экспорт", f"Результаты экспортированы в:\n{filepath}")
    
    def rescan_selected(self):
        """Пересканировать выбранное устройство"""
        selected = self.devices_table.currentRow()
        if selected >= 0:
            device = self.devices[selected]
            QMessageBox.information(self, "Пересканирование", 
                f"Пересканирование устройства:\n{device['hostname']} ({device['ip']})")
    
    def show_device_actions(self, device):
        """Показать действия для устройства"""
        from PyQt6.QtWidgets import QMenu
        
        menu = QMenu(self)
        
        menu.addAction(f"📋 Информация о {device['hostname']}").triggered.connect(
            lambda: self.show_device_info(device))
        
        menu.addSeparator()
        
        menu.addAction("🔍 Пересканировать").triggered.connect(
            lambda: self.rescan_device(device))
        
        menu.addAction("🏷️ Изменить тип").triggered.connect(
            lambda: self.change_device_type(device))
        
        menu.addSeparator()
        
        menu.addAction("🎨 Добавить в конструктор").triggered.connect(
            lambda: self.add_to_constructor(device))
        
        menu.exec(self.mapToGlobal(self.sender().pos()))
    
    def show_device_info(self, device):
        """Показать подробную информацию об устройстве"""
        info_text = f"""
        <h2>{device['icon']} {device['hostname']}</h2>
        <hr>
        <table width="100%">
        <tr><td><b>IP адрес:</b></td><td>{device['ip']}</td></tr>
        <tr><td><b>MAC адрес:</b></td><td>{device['mac']}</td></tr>
        <tr><td><b>Производитель:</b></td><td>{device['vendor']}</td></tr>
        <tr><td><b>Тип:</b></td><td>{device['type']}</td></tr>
        <tr><td><b>Статус:</b></td><td>{device['status']}</td></tr>
        <tr><td><b>Уровень риска:</b></td><td>{device['risk']}</td></tr>
        <tr><td><b>Открытые порты:</b></td><td>{', '.join(map(str, device['ports']))}</td></tr>
        <tr><td><b>Обнаружено:</b></td><td>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
        </table>
        """
        
        msg = QMessageBox()
        msg.setWindowTitle(f"Информация: {device['hostname']}")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(info_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
    
    def change_device_type(self, device):
        """Изменить тип устройства"""
        types = ["computer", "router", "iot", "printer", "camera", "phone", "server", "unknown"]
        type_names = {
            "computer": "💻 Компьютер",
            "router": "🌐 Роутер",
            "iot": "💡 Умное устройство",
            "printer": "🖨️ Принтер",
            "camera": "📷 Камера",
            "phone": "📱 Телефон",
            "server": "🖥️ Сервер",
            "unknown": "❓ Неизвестно"
        }
        
        current_type = type_names.get(device["type"], device["type"])
        
        new_type, ok = QInputDialog.getItem(
            self, "Изменить тип устройства",
            f"Выберите новый тип для {device['hostname']}:",
            list(type_names.values()),
            list(type_names.values()).index(current_type),
            False
        )
        
        if ok and new_type:
            # Находим ключ по значению
            for key, value in type_names.items():
                if value == new_type:
                    device["type"] = key
                    # Обновляем таблицу
                    self.on_scan_completed(self.devices)
                    break
    
    def add_to_constructor(self, device):
        """Добавить устройство в конструктор"""
        QMessageBox.information(self, "Добавление в конструктор",
            f"Устройство {device['hostname']} добавлено в конструктор политик.\n"
            "Перейдите в раздел 🎨 Конструктор для настройки правил.")
    
    def show_settings(self):
        """Показать настройки сканирования"""
        from PyQt6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Настройки сканирования")
        dialog.setFixedSize(400, 300)
        
        layout = QFormLayout(dialog)
        
        # Параметры сканирования
        timeout_input = QLineEdit("1000")
        timeout_input.setPlaceholderText("мс")
        
        threads_input = QLineEdit("10")
        
        retries_input = QLineEdit("2")
        
        layout.addRow("Таймаут (мс):", timeout_input)
        layout.addRow("Потоки:", threads_input)
        layout.addRow("Повторные попытки:", retries_input)
        
        # Дополнительные опции
        os_detection = QCheckBox("Определение ОС")
        os_detection.setChecked(True)
        
        service_detection = QCheckBox("Определение сервисов")
        service_detection.setChecked(True)
        
        version_detection = QCheckBox("Определение версий")
        
        layout.addRow("", os_detection)
        layout.addRow("", service_detection)
        layout.addRow("", version_detection)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Настройки", "Настройки сканирования сохранены!")
