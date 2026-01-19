"""
Главное окно ZeroTrust Inspector с реальным drag-and-drop
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QMessageBox,
    QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem,
    QTabWidget, QSplitter, QGroupBox, QFrame, QTextEdit,
    QDialog, QLineEdit, QComboBox, QFormLayout, QDialogButtonBox,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QGraphicsEllipseItem, QGraphicsItem, QMenu, QInputDialog,
    QFileDialog, QApplication
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, QThread, QPointF, QRectF,
    QMimeData, QByteArray, QDataStream, QIODevice
)
from PyQt6.QtGui import (
    QIcon, QFont, QBrush, QColor, QPen, QPainter,
    QDrag, QCursor, QAction, QPixmap
)

from ..core.models import (
    NetworkDevice, SecurityZone, ZoneType, DeviceType,
    ActionType, SecurityRule, NetworkPolicy
)
from ..core.scanner import NetworkScanner
from ..core.generator import PolicyGenerator

class ScanThread(QThread):
    """Поток для сканирования сети"""
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, scanner: NetworkScanner):
        super().__init__()
        self.scanner = scanner
    
    def run(self):
        """Запуск сканирования"""
        try:
            devices = self.scanner.quick_scan()
            self.finished.emit(devices)
        except Exception as e:
            self.error.emit(str(e))

class DeviceItem(QGraphicsEllipseItem):
    """Элемент устройства на канвасе с поддержкой drag-and-drop"""
    
    def __init__(self, device: NetworkDevice, x: float, y: float):
        super().__init__(0, 0, 60, 60)
        self.device = device
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("#2196F3")))
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        
        # Добавляем текст
        self.text = QGraphicsTextItem(device.display_name, self)
        self.text.setPos(10, 20)
        self.text.setDefaultTextColor(Qt.GlobalColor.white)
        
        # Устанавливаем цвет по типу устройства
        self.set_device_color()
        
        # Для drag-and-drop
        self.drag_start_position = None
    
    def set_device_color(self):
        """Установить цвет в зависимости от типа устройства"""
        color_map = {
            DeviceType.ROUTER: QColor("#F44336"),    # Красный
            DeviceType.COMPUTER: QColor("#4CAF50"),  # Зеленый
            DeviceType.PHONE: QColor("#2196F3"),     # Синий
            DeviceType.IOT: QColor("#FF9800"),       # Оранжевый
            DeviceType.PRINTER: QColor("#9C27B0"),   # Фиолетовый
            DeviceType.CAMERA: QColor("#795548"),    # Коричневый
            DeviceType.TV: QColor("#607D8B"),        # Серый
        }
        color = color_map.get(self.device.device_type, QColor("#9E9E9E"))
        self.setBrush(QBrush(color))
    
    def mousePressEvent(self, event):
        """Обработка нажатия мыши - начало drag"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.scenePos()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Обработка перемещения мыши - начало drag операции"""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        
        if self.drag_start_position is not None:
            # Проверяем, началось ли перетаскивание
            manhattan_length = (event.scenePos() - self.drag_start_position).manhattanLength()
            if manhattan_length < QApplication.startDragDistance():
                return
            
            # Создаем drag операцию
            drag = QDrag(event.widget())
            mime_data = QMimeData()
            
            # Сохраняем данные об устройстве
            device_data = {
                'ip': self.device.ip_address,
                'type': 'device'
            }
            
            import pickle
            mime_data.setData('application/device-data', pickle.dumps(device_data))
            drag.setMimeData(mime_data)
            
            # Создаем изображение для перетаскивания
            pixmap = QPixmap(60, 60)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setBrush(self.brush())
            painter.setPen(self.pen())
            painter.drawEllipse(0, 0, 60, 60)
            painter.drawText(10, 30, self.device.display_name[:8])
            painter.end()
            
            drag.setPixmap(pixmap)
            drag.setHotSpot(QPoint(30, 30))
            
            # Запускаем drag операцию
            drag.exec(Qt.DropAction.MoveAction)
            
            # После перетаскивания восстанавливаем позицию
            self.setPos(self.x(), self.y())
    
    def mouseReleaseEvent(self, event):
        """Обработка отпускания мыши"""
        self.drag_start_position = None
        super().mouseReleaseEvent(event)
        
class ZoneItem(QGraphicsRectItem):
    """Элемент зоны на канвасе с поддержкой drop"""
    
    def __init__(self, zone: SecurityZone):
        super().__init__(0, 0, zone.size[0], zone.size[1])
        self.zone = zone
        self.setPos(zone.position[0], zone.position[1])
        self.setBrush(QBrush(QColor(zone.color)))
        self.setPen(QPen(Qt.GlobalColor.black, 3))
        self.setOpacity(0.7)
        self.setAcceptDrops(True)
        
        # Добавляем текст с названием зоны
        self.text = QGraphicsTextItem(zone.name, self)
        self.text.setPos(10, 10)
        self.text.setDefaultTextColor(Qt.GlobalColor.white)
        
        # Список устройств в зоне
        self.device_items = []
        
        # Подсветка при drag-over
        self.highlight_brush = QBrush(QColor(zone.color).lighter(150))
        self.normal_brush = QBrush(QColor(zone.color))
    
    def dragEnterEvent(self, event):
        """Обработка входа drag операции в зону"""
        if event.mimeData().hasFormat('application/device-data'):
            event.acceptProposedAction()
            self.setBrush(self.highlight_brush)
    
    def dragLeaveEvent(self, event):
        """Обработка выхода drag операции из зоны"""
        self.setBrush(self.normal_brush)
    
    def dropEvent(self, event):
        """Обработка drop операции"""
        if event.mimeData().hasFormat('application/device-data'):
            import pickle
            device_data = pickle.loads(event.mimeData().data('application/device-data'))
            
            # Эмитируем сигнал о том, что устройство было перетащено в зону
            scene = self.scene()
            if scene and hasattr(scene.parent(), 'device_dropped'):
                # Ищем устройство по IP
                for item in scene.items():
                    if isinstance(item, DeviceItem) and item.device.ip_address == device_data['ip']:
                        # Испускаем сигнал через канвас
                        self.scene().parent().device_dropped.emit(item.device, self.zone)
                        break
            
            event.acceptProposedAction()
            self.setBrush(self.normal_brush)
class NetworkCanvas(QGraphicsView):
    """Канвас для визуализации сети"""
    
    device_dropped = pyqtSignal(NetworkDevice, SecurityZone)
    
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setAcceptDrops(True)
        
        self.zone_items = {}
        self.device_items = {}
        
        # Настройка фона
        self.setBackgroundBrush(QBrush(QColor("#f0f0f0")))
    
    def add_zone(self, zone: SecurityZone):
        """Добавить зону на канвас"""
        zone_item = ZoneItem(zone)
        self.scene.addItem(zone_item)
        self.zone_items[zone.name] = zone_item
    
    def add_device(self, device: NetworkDevice, zone: Optional[SecurityZone] = None):
        """Добавить устройство на канвас"""
        device_item = DeviceItem(device, 50, 50)
        self.scene.addItem(device_item)
        self.device_items[device.ip_address] = device_item
        
        if zone and zone.name in self.zone_items:
            self.zone_items[zone.name].add_device(device_item)
    
    def remove_device(self, device: NetworkDevice):
        """Удалить устройство с канваса"""
        if device.ip_address in self.device_items:
            item = self.device_items[device.ip_address]
            self.scene.removeItem(item)
            del self.device_items[device.ip_address]
    
    def clear_all(self):
        """Очистить канвас"""
        self.scene.clear()
        self.zone_items.clear()
        self.device_items.clear()

class ZoneDialog(QDialog):
    """Диалог создания/редактирования зоны"""
    
    def __init__(self, parent=None, zone: SecurityZone = None):
        super().__init__(parent)
        self.zone = zone
        
        self.setWindowTitle("Зона безопасности" if zone else "Новая зона")
        self.setModal(True)
        
        layout = QFormLayout(self)
        
        # Название зоны
        self.name_edit = QLineEdit(zone.name if zone else "")
        layout.addRow("Название:", self.name_edit)
        
        # Тип зоны
        self.type_combo = QComboBox()
        for zone_type in ZoneType:
            self.type_combo.addItem(zone_type.value.capitalize(), zone_type)
        
        if zone:
            index = self.type_combo.findData(zone.zone_type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        
        layout.addRow("Тип зоны:", self.type_combo)
        
        # Описание
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(100)
        if zone:
            self.desc_edit.setText(zone.description)
        layout.addRow("Описание:", self.desc_edit)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def get_zone_data(self) -> tuple:
        """Получить данные зоны"""
        name = self.name_edit.text().strip()
        zone_type = self.type_combo.currentData()
        description = self.desc_edit.toPlainText().strip()
        return name, zone_type, description

class RuleDialog(QDialog):
    """Диалог создания правила"""
    
    def __init__(self, parent=None, zones: List[str] = None, rule: SecurityRule = None):
        super().__init__(parent)
        
        self.setWindowTitle("Правило безопасности" if rule else "Новое правило")
        self.setModal(True)
        
        layout = QFormLayout(self)
        
        # Исходная зона
        self.source_combo = QComboBox()
        if zones:
            self.source_combo.addItems(zones)
        layout.addRow("Исходная зона:", self.source_combo)
        
        # Целевая зона
        self.dest_combo = QComboBox()
        if zones:
            self.dest_combo.addItems(zones)
        layout.addRow("Целевая зона:", self.dest_combo)
        
        # Действие
        self.action_combo = QComboBox()
        self.action_combo.addItem("Разрешить", ActionType.ALLOW)
        self.action_combo.addItem("Запретить", ActionType.DENY)
        layout.addRow("Действие:", self.action_combo)
        
        # Протокол
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["any", "tcp", "udp", "icmp"])
        layout.addRow("Протокол:", self.protocol_combo)
        
        # Описание
        self.desc_edit = QLineEdit()
        if rule:
            self.desc_edit.setText(rule.description)
        layout.addRow("Описание:", self.desc_edit)
        
        # Заполняем данные правила, если оно передано
        if rule:
            index = self.source_combo.findText(rule.source_zone)
            if index >= 0:
                self.source_combo.setCurrentIndex(index)
            
            index = self.dest_combo.findText(rule.destination_zone)
            if index >= 0:
                self.dest_combo.setCurrentIndex(index)
            
            index = self.action_combo.findData(rule.action)
            if index >= 0:
                self.action_combo.setCurrentIndex(index)
            
            index = self.protocol_combo.findText(rule.protocol)
            if index >= 0:
                self.protocol_combo.setCurrentIndex(index)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def get_rule_data(self) -> dict:
        """Получить данные правила"""
        return {
            'source': self.source_combo.currentText(),
            'dest': self.dest_combo.currentText(),
            'action': self.action_combo.currentData(),
            'protocol': self.protocol_combo.currentText(),
            'description': self.desc_edit.text().strip()
        }

class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        
        # Инициализация компонентов
        self.scanner = NetworkScanner()
        self.generator = PolicyGenerator()
        self.current_policy = NetworkPolicy("Новая политика")
        self.devices = []
        
        self.setup_ui()
        self.setup_connections()
        self.create_default_zones()
        
        self.setWindowTitle("ZeroTrust Inspector v1.0.0")
        self.setGeometry(100, 100, 1400, 900)
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Панель инструментов
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)
        
        # Основная область
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель - устройства
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Центральная панель - визуализация
        center_panel = self.create_center_panel()
        splitter.addWidget(center_panel)
        
        # Правая панель - правила и детали
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([300, 700, 400])
        main_layout.addWidget(splitter)
        
        # Статус бар
        self.status_bar = self.statusBar()
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.hide()
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def create_toolbar(self) -> QWidget:
        """Создать панель инструментов"""
        toolbar = QWidget()
        layout = QHBoxLayout(toolbar)
        
        # Кнопки
        self.btn_scan = QPushButton("🔍 Сканировать сеть")
        self.btn_scan.setToolTip("Сканировать локальную сеть")
        
        self.btn_add_zone = QPushButton("➕ Добавить зону")
        self.btn_add_zone.setToolTip("Добавить новую зону безопасности")
        
        self.btn_add_rule = QPushButton("📝 Добавить правило")
        self.btn_add_rule.setToolTip("Добавить правило безопасности")
        
        self.btn_export = QPushButton("📤 Экспорт")
        self.btn_export.setToolTip("Экспортировать конфигурацию")
        
        self.btn_validate = QPushButton("✅ Валидировать")
        self.btn_validate.setToolTip("Проверить политику безопасности")
        
        self.btn_save = QPushButton("💾 Сохранить")
        self.btn_save.setToolTip("Сохранить политику")
        
        self.btn_load = QPushButton("📂 Загрузить")
        self.btn_load.setToolTip("Загрузить политику")
        
        layout.addWidget(self.btn_scan)
        layout.addWidget(self.btn_add_zone)
        layout.addWidget(self.btn_add_rule)
        layout.addWidget(self.btn_export)
        layout.addWidget(self.btn_validate)
        layout.addWidget(self.btn_save)
        layout.addWidget(self.btn_load)
        layout.addStretch()
        
        return toolbar
    
    def create_left_panel(self) -> QWidget:
        """Создать левую панель (устройства)"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Группа устройств
        group = QGroupBox("Обнаруженные устройства")
        group_layout = QVBoxLayout()
        
        self.device_list = QTreeWidget()
        self.device_list.setHeaderLabels(["Устройство", "IP", "Тип", "Зона"])
        self.device_list.setSortingEnabled(True)
        self.device_list.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        
        group_layout.addWidget(self.device_list)
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        # Кнопки управления устройствами
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Обновить")
        self.btn_classify = QPushButton("Автоклассификация")
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_classify)
        layout.addLayout(btn_layout)
        
        return panel
    
    def create_center_panel(self) -> QWidget:
        """Создать центральную панель (визуализация)"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Заголовок
        title = QLabel("Визуализация сети Zero Trust")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Канвас
        self.canvas = NetworkCanvas()
        layout.addWidget(self.canvas)
        
        # Подсказка
        hint = QLabel("Перетаскивайте устройства на зоны для распределения")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(hint)
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Создать правую панель (правила и детали)"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Вкладки
        tabs = QTabWidget()
        
        # Вкладка зон
        zones_tab = self.create_zones_tab()
        tabs.addTab(zones_tab, "Зоны")
        
        # Вкладка правил
        rules_tab = self.create_rules_tab()
        tabs.addTab(rules_tab, "Правила")
        
        # Вкладка деталей
        details_tab = self.create_details_tab()
        tabs.addTab(details_tab, "Детали")
        
        # Вкладка экспорта
        export_tab = self.create_export_tab()
        tabs.addTab(export_tab, "Экспорт")
        
        layout.addWidget(tabs)
        
        return panel
    
    def create_zones_tab(self) -> QWidget:
        """Создать вкладку зон"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.zones_list = QListWidget()
        layout.addWidget(self.zones_list)
        
        # Кнопки управления зонами
        btn_layout = QHBoxLayout()
        self.btn_edit_zone = QPushButton("✏️ Редактировать")
        self.btn_delete_zone = QPushButton("🗑️ Удалить")
        btn_layout.addWidget(self.btn_edit_zone)
        btn_layout.addWidget(self.btn_delete_zone)
        layout.addLayout(btn_layout)
        
        return tab
    
    def create_rules_tab(self) -> QWidget:
        """Создать вкладку правил"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.rules_list = QTreeWidget()
        self.rules_list.setHeaderLabels(["Источник", "Назначение", "Действие", "Протокол", "Описание"])
        self.rules_list.setSortingEnabled(True)
        layout.addWidget(self.rules_list)
        
        # Кнопки управления правилами
        btn_layout = QHBoxLayout()
        self.btn_edit_rule = QPushButton("✏️ Редактировать")
        self.btn_delete_rule = QPushButton("🗑️ Удалить")
        btn_layout.addWidget(self.btn_edit_rule)
        btn_layout.addWidget(self.btn_delete_rule)
        layout.addLayout(btn_layout)
        
        return tab
    
    def create_details_tab(self) -> QWidget:
        """Создать вкладку деталей"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        layout.addWidget(self.details_text)
        
        return tab
    
    def create_export_tab(self) -> QWidget:
        """Создать вкладку экспорта"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Выбор платформы
        platform_layout = QHBoxLayout()
        platform_layout.addWidget(QLabel("Платформа:"))
        
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["OpenWrt", "iptables", "Windows Firewall"])
        platform_layout.addWidget(self.platform_combo)
        
        self.btn_generate = QPushButton("Сгенерировать")
        platform_layout.addWidget(self.btn_generate)
        platform_layout.addStretch()
        
        layout.addLayout(platform_layout)
        
        # Поле с конфигурацией
        self.config_text = QTextEdit()
        self.config_text.setReadOnly(True)
        layout.addWidget(self.config_text)
        
        # Кнопки экспорта
        export_layout = QHBoxLayout()
        self.btn_copy = QPushButton("Копировать")
        self.btn_save_file = QPushButton("Сохранить в файл")
        export_layout.addWidget(self.btn_copy)
        export_layout.addWidget(self.btn_save_file)
        layout.addLayout(export_layout)
        
        return tab
    
    def setup_connections(self):
        """Настроить соединения"""
        # Кнопки
        self.btn_scan.clicked.connect(self.start_scan)
        self.btn_add_zone.clicked.connect(self.add_zone)
        self.btn_add_rule.clicked.connect(self.add_rule)
        self.btn_export.clicked.connect(self.show_export_tab)
        self.btn_validate.clicked.connect(self.validate_policy)
        self.btn_save.clicked.connect(self.save_policy)
        self.btn_load.clicked.connect(self.load_policy)
        
        # Управление зонами
        self.btn_edit_zone.clicked.connect(self.edit_zone)
        self.btn_delete_zone.clicked.connect(self.delete_zone)
        
        # Управление правилами
        self.btn_edit_rule.clicked.connect(self.edit_rule)
        self.btn_delete_rule.clicked.connect(self.delete_rule)
        
        # Управление устройствами
        self.btn_refresh.clicked.connect(self.refresh_devices)
        self.btn_classify.clicked.connect(self.auto_classify)
        
        # Экспорт
        self.btn_generate.clicked.connect(self.generate_config)
        self.btn_copy.clicked.connect(self.copy_config)
        self.btn_save_file.clicked.connect(self.save_config_file)
        
        # Списки
        self.device_list.itemClicked.connect(self.show_device_details)
        self.zones_list.itemClicked.connect(self.show_zone_details)
        self.rules_list.itemClicked.connect(self.show_rule_details)
        
        # Канвас
        self.canvas.device_dropped.connect(self.on_device_dropped)
    
    def create_default_zones(self):
        """Создать зоны по умолчанию"""
        default_zones = [
            SecurityZone("Доверенная зона", ZoneType.TRUSTED, "Компьютеры и телефоны"),
            SecurityZone("IoT устройства", ZoneType.IOT, "Умные устройства и камеры"),
            SecurityZone("Гостевая сеть", ZoneType.GUEST, "Гостевые устройства"),
            SecurityZone("Серверы", ZoneType.SERVER, "Серверы и NAS"),
        ]
        
        for zone in default_zones:
            self.current_policy.add_zone(zone)
            self.update_zones_list()
            self.canvas.add_zone(zone)
    
    def start_scan(self):
        """Запустить сканирование сети"""
        self.progress_bar.show()
        self.status_bar.showMessage("Сканирование сети...")
        
        self.scan_thread = ScanThread(self.scanner)
        self.scan_thread.progress.connect(self.on_scan_progress)
        self.scan_thread.finished.connect(self.on_scan_finished)
        self.scan_thread.error.connect(self.on_scan_error)
        self.scan_thread.start()
        
        self.btn_scan.setEnabled(False)
    
    def on_scan_progress(self, message: str, progress: int):
        """Обновить прогресс сканирования"""
        self.progress_bar.setValue(progress)
        self.status_bar.showMessage(message)
    
    def on_scan_finished(self, devices: List[NetworkDevice]):
        """Обработка завершения сканирования"""
        self.devices = devices
        self.update_device_list()
        
        # Автоматически распределяем устройства по зонам
        self.auto_classify()
        
        self.progress_bar.hide()
        self.status_bar.showMessage(f"Найдено {len(devices)} устройств")
        self.btn_scan.setEnabled(True)
        
        QMessageBox.information(
            self,
            "Сканирование завершено",
            f"Найдено {len(devices)} устройств в сети"
        )
    
    def on_scan_error(self, error: str):
        """Обработка ошибки сканирования"""
        self.progress_bar.hide()
        self.status_bar.showMessage(f"Ошибка: {error}")
        self.btn_scan.setEnabled(True)
        
        QMessageBox.critical(self, "Ошибка сканирования", error)
    
    def update_device_list(self):
        """Обновить список устройств"""
        self.device_list.clear()
        
        for device in self.devices:
            # Находим зону устройства
            zone_name = "Не распределено"
            for zone in self.current_policy.zones.values():
                if device in zone.devices:
                    zone_name = zone.name
                    break
            
            item = QTreeWidgetItem([
                device.display_name,
                device.ip_address,
                device.device_type.value,
                zone_name
            ])
            
            # Устанавливаем цвет в зависимости от типа устройства
            self.set_device_item_color(item, device.device_type)
            
            self.device_list.addTopLevelItem(item)
    
    def set_device_item_color(self, item: QTreeWidgetItem, device_type: DeviceType):
        """Установить цвет элемента списка устройств"""
        color_map = {
            DeviceType.ROUTER: QColor("#F44336"),
            DeviceType.COMPUTER: QColor("#4CAF50"),
            DeviceType.PHONE: QColor("#2196F3"),
            DeviceType.IOT: QColor("#FF9800"),
            DeviceType.PRINTER: QColor("#9C27B0"),
        }
        
        color = color_map.get(device_type, QColor("#9E9E9E"))
        for i in range(item.columnCount()):
            item.setForeground(i, color)
    
    def update_zones_list(self):
        """Обновить список зон"""
        self.zones_list.clear()
        
        for zone_name in self.current_policy.zones:
            item = QListWidgetItem(zone_name)
            zone = self.current_policy.zones[zone_name]
            item.setBackground(QColor(zone.color))
            item.setForeground(Qt.GlobalColor.white)
            self.zones_list.addItem(item)
    
    def update_rules_list(self):
        """Обновить список правил"""
        self.rules_list.clear()
        
        for rule in self.current_policy.rules:
            item = QTreeWidgetItem([
                rule.source_zone,
                rule.destination_zone,
                rule.action.value,
                rule.protocol,
                rule.description
            ])
            
            # Устанавливаем цвет в зависимости от действия
            if rule.action == ActionType.ALLOW:
                item.setForeground(2, QColor("#4CAF50"))
            else:
                item.setForeground(2, QColor("#F44336"))
            
            self.rules_list.addTopLevelItem(item)
    
    def add_zone(self):
        """Добавить новую зону"""
        dialog = ZoneDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, zone_type, description = dialog.get_zone_data()
            
            if not name:
                QMessageBox.warning(self, "Ошибка", "Введите название зоны")
                return
            
            if name in self.current_policy.zones:
                QMessageBox.warning(self, "Ошибка", "Зона с таким названием уже существует")
                return
            
            zone = SecurityZone(name, zone_type, description)
            zone.position = (len(self.current_policy.zones) * 220, 50)
            
            self.current_policy.add_zone(zone)
            self.update_zones_list()
            self.canvas.add_zone(zone)
            
            self.status_bar.showMessage(f"Добавлена зона: {name}")
    
    def edit_zone(self):
        """Редактировать выбранную зону"""
        selected = self.zones_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите зону для редактирования")
            return
        
        zone_name = selected.text()
        zone = self.current_policy.zones.get(zone_name)
        if not zone:
            return
        
        dialog = ZoneDialog(self, zone)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, zone_type, description = dialog.get_zone_data()
            
            if name != zone_name and name in self.current_policy.zones:
                QMessageBox.warning(self, "Ошибка", "Зона с таким названием уже существует")
                return
            
            # Обновляем зону
            zone.name = name
            zone.zone_type = zone_type
            zone.description = description
            
            # Если имя изменилось, нужно обновить ключ в словаре
            if name != zone_name:
                self.current_policy.zones[name] = zone
                del self.current_policy.zones[zone_name]
                
                # Обновляем ссылки в правилах
                for rule in self.current_policy.rules:
                    if rule.source_zone == zone_name:
                        rule.source_zone = name
                    if rule.destination_zone == zone_name:
                        rule.destination_zone = name
            
            self.update_zones_list()
            self.update_rules_list()
            self.update_canvas()
            
            self.status_bar.showMessage(f"Обновлена зона: {name}")
    
    def delete_zone(self):
        """Удалить выбранную зону"""
        selected = self.zones_list.currentItem()
        if not selected:
            return
        
        zone_name = selected.text()
        
        reply = QMessageBox.question(
            self,
            "Удаление зоны",
            f"Удалить зону '{zone_name}' и все связанные правила?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.current_policy.remove_zone(zone_name)
            self.update_zones_list()
            self.update_rules_list()
            self.update_canvas()
            
            self.status_bar.showMessage(f"Удалена зона: {zone_name}")
    
    def add_rule(self):
        """Добавить новое правило"""
        if not self.current_policy.zones:
            QMessageBox.warning(self, "Ошибка", "Сначала создайте зоны безопасности")
            return
        
        dialog = RuleDialog(self, list(self.current_policy.zones.keys()))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_rule_data()
            
            rule = SecurityRule(
                source_zone=data['source'],
                destination_zone=data['dest'],
                action=data['action'],
                protocol=data['protocol'],
                description=data['description']
            )
            
            self.current_policy.add_rule(rule)
            self.update_rules_list()
            
            self.status_bar.showMessage(f"Добавлено правило: {data['source']} → {data['dest']}")
    
    def edit_rule(self):
        """Редактировать выбранное правило"""
        selected = self.rules_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите правило для редактирования")
            return
        
        index = self.rules_list.indexOfTopLevelItem(selected)
        if index < 0 or index >= len(self.current_policy.rules):
            return
        
        rule = self.current_policy.rules[index]
        dialog = RuleDialog(self, list(self.current_policy.zones.keys()), rule)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_rule_data()
            
            # Обновляем правило
            rule.source_zone = data['source']
            rule.destination_zone = data['dest']
            rule.action = data['action']
            rule.protocol = data['protocol']
            rule.description = data['description']
            
            self.update_rules_list()
            self.status_bar.showMessage("Правило обновлено")
    
    def delete_rule(self):
        """Удалить выбранное правило"""
        selected = self.rules_list.currentItem()
        if not selected:
            return
        
        index = self.rules_list.indexOfTopLevelItem(selected)
        if 0 <= index < len(self.current_policy.rules):
            rule = self.current_policy.rules[index]
            
            reply = QMessageBox.question(
                self,
                "Удаление правила",
                f"Удалить правило '{rule.description}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.current_policy.rules.pop(index)
                self.update_rules_list()
                self.status_bar.showMessage("Правило удалено")
    
    def auto_classify(self):
        """Автоматически классифицировать устройства по зонам"""
        if not self.devices:
            QMessageBox.warning(self, "Ошибка", "Сначала выполните сканирование сети")
            return
        
        # Очищаем все зоны
        for zone in self.current_policy.zones.values():
            zone.devices.clear()
        
        # Распределяем устройства по зонам
        for device in self.devices:
            if device.device_type in [DeviceType.COMPUTER, DeviceType.PHONE]:
                zone_name = "Доверенная зона"
            elif device.device_type in [DeviceType.IOT, DeviceType.CAMERA, DeviceType.TV]:
                zone_name = "IoT устройства"
            elif device.device_type == DeviceType.ROUTER:
                zone_name = "Серверы"
            else:
                zone_name = "Гостевая сеть"
            
            zone = self.current_policy.zones.get(zone_name)
            if zone:
                zone.add_device(device)
        
        # Обновляем интерфейс
        self.update_device_list()
        self.update_canvas()
        self.status_bar.showMessage("Устройства распределены по зонам")
    
    def refresh_devices(self):
        """Обновить список устройств"""
        self.update_device_list()
    
    def show_device_details(self, item: QTreeWidgetItem, column: int):
        """Показать детали устройства"""
        ip = item.text(1)
        device = next((d for d in self.devices if d.ip_address == ip), None)
        
        if device:
            details = f"""
            <h3>Информация об устройстве</h3>
            <p><b>Имя:</b> {device.display_name}</p>
            <p><b>IP адрес:</b> {device.ip_address}</p>
            <p><b>MAC адрес:</b> {device.mac_address or 'Неизвестно'}</p>
            <p><b>Тип:</b> {device.device_type.value}</p>
            <p><b>Производитель:</b> {device.vendor or 'Неизвестно'}</p>
            <p><b>Открытые порты:</b> {', '.join(map(str, device.open_ports))}</p>
            <p><b>ОС:</b> {device.os_info or 'Неизвестно'}</p>
            <p><b>Оценка риска:</b> {device.risk_score:.1f}/1.0</p>
            <p><b>Шлюз:</b> {'Да' if device.is_gateway else 'Нет'}</p>
            """
            self.details_text.setHtml(details)
    
    def show_zone_details(self, item: QListWidgetItem):
        """Показать детали зоны"""
        zone_name = item.text()
        zone = self.current_policy.zones.get(zone_name)
        
        if zone:
            details = f"""
            <h3>Информация о зоне</h3>
            <p><b>Название:</b> {zone.name}</p>
            <p><b>Тип:</b> {zone.zone_type.value}</p>
            <p><b>Описание:</b> {zone.description}</p>
            <p><b>Количество устройств:</b> {zone.device_count}</p>
            <p><b>Устройства:</b></p>
            <ul>
            """
            
            for device in zone.devices:
                details += f"<li>{device.display_name} ({device.ip_address})</li>"
            
            details += "</ul>"
            self.details_text.setHtml(details)
    
    def show_rule_details(self, item: QTreeWidgetItem, column: int):
        """Показать детали правила"""
        source = item.text(0)
        dest = item.text(1)
        action = item.text(2)
        
        details = f"""
        <h3>Информация о правиле</h3>
        <p><b>Источник:</b> {source}</p>
        <p><b>Назначение:</b> {dest}</p>
        <p><b>Действие:</b> {action}</p>
        <p><b>Протокол:</b> {item.text(3)}</p>
        <p><b>Описание:</b> {item.text(4)}</p>
        """
        self.details_text.setHtml(details)
    
    def update_canvas(self):
        """Обновить канвас"""
        self.canvas.clear_all()
        
        # Добавляем зоны
        for zone in self.current_policy.zones.values():
            self.canvas.add_zone(zone)
            
            # Добавляем устройства этой зоны
            for device in zone.devices:
                self.canvas.add_device(device, zone)
    
    def on_device_dropped(self, device: NetworkDevice, zone: SecurityZone):
        """Обработка перетаскивания устройства на зону"""
        # Удаляем устройство из всех зон
        for z in self.current_policy.zones.values():
            z.remove_device(device)
        
        # Добавляем в новую зону
        zone.add_device(device)
        
        # Обновляем интерфейс
        self.update_device_list()
        self.update_canvas()
        
        self.status_bar.showMessage(f"Устройство {device.display_name} перемещено в зону {zone.name}")
    
    def validate_policy(self):
        """Валидация политики"""
        errors = self.current_policy.validate()
        
        if errors:
            error_text = "<h3>Обнаружены ошибки:</h3><ul>"
            for error in errors:
                error_text += f"<li>{error}</li>"
            error_text += "</ul>"
            
            QMessageBox.warning(self, "Ошибки валидации", error_text)
        else:
            QMessageBox.information(
                self,
                "Валидация успешна",
                "Политика безопасности корректна"
            )
    
    def save_policy(self):
        """Сохранить политику в файл"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить политику",
            "exports/policy.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                self.current_policy.save_to_file(file_path)
                self.status_bar.showMessage(f"Политика сохранена: {file_path}")
                QMessageBox.information(self, "Сохранено", "Политика успешно сохранена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить политику: {e}")
    
    def load_policy(self):
        """Загрузить политику из файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить политику",
            "exports",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                self.current_policy = NetworkPolicy.load_from_file(file_path)
                
                # Обновляем интерфейс
                self.update_zones_list()
                self.update_rules_list()
                self.update_canvas()
                
                self.status_bar.showMessage(f"Политика загружена: {file_path}")
                QMessageBox.information(self, "Загружено", "Политика успешно загружена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить политику: {e}")
    
    def show_export_tab(self):
        """Показать вкладку экспорта"""
        self.tab_widget = self.centralWidget().findChild(QTabWidget)
        if self.tab_widget:
            self.tab_widget.setCurrentIndex(3)  # Индекс вкладки экспорта
    
    def generate_config(self):
        """Сгенерировать конфигурацию"""
        platform = self.platform_combo.currentText().lower()
        
        try:
            if platform == "openwrt":
                config = self.generator.generate_openwrt_config(self.current_policy)
            elif platform == "iptables":
                config = self.generator.generate_iptables_config(self.current_policy)
            elif "windows" in platform:
                config = self.generator.generate_windows_firewall(self.current_policy)
            else:
                QMessageBox.warning(self, "Ошибка", f"Неподдерживаемая платформа: {platform}")
                return
            
            self.config_text.setPlainText(config)
            self.status_bar.showMessage(f"Конфигурация для {platform} сгенерирована")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сгенерировать конфигурацию: {e}")
    
    def copy_config(self):
        """Копировать конфигурацию в буфер обмена"""
        config = self.config_text.toPlainText()
        if config:
            QApplication.clipboard().setText(config)
            self.status_bar.showMessage("Конфигурация скопирована в буфер обмена")
    
    def save_config_file(self):
        """Сохранить конфигурацию в файл"""
        config = self.config_text.toPlainText()
        if not config:
            QMessageBox.warning(self, "Ошибка", "Сначала сгенерируйте конфигурацию")
            return
        
        platform = self.platform_combo.currentText().lower()
        extensions = {
            "openwrt": "conf",
            "iptables": "sh",
            "windows": "ps1"
        }
        
        ext = extensions.get(platform, "txt")
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить конфигурацию",
            f"exports/config.{ext}",
            f"Config Files (*.{ext})"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(config)
                
                self.status_bar.showMessage(f"Конфигурация сохранена: {file_path}")
                QMessageBox.information(self, "Сохранено", "Конфигурация успешно сохранена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить конфигурацию: {e}")