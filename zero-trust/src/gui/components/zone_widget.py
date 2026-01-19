"""
Виджет зоны безопасности для отображения на холсте
"""

from PyQt6.QtWidgets import QGraphicsItem, QMenu
from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QBrush, QPen, QColor, QFont, QPainterPath,
    QMouseEvent
)

from ...core.models import SecurityZone, NetworkDevice
from ...core.constants import ZONE_COLORS
from .device_item import DeviceItem

class ZoneWidget(QGraphicsItem):
    """Графический элемент зоны безопасности"""
    
    device_added = pyqtSignal(NetworkDevice)
    device_removed = pyqtSignal(NetworkDevice)
    
    def __init__(self, zone: SecurityZone, x: float = 0, y: float = 0):
        super().__init__()
        self.zone = zone
        self.device_items = []
        self.setPos(x, y)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setAcceptDrops(True)
        
        # Цвет зоны
        self.color = QColor(zone.color)
        if self.color == QColor("#FFFFFF"):
            # Используем цвет по умолчанию из констант
            default_color = ZONE_COLORS.get(zone.zone_type.value, "#E6E6FA")
            self.color = QColor(default_color)
        
        self.width = 250
        self.height = 200
        self.device_spacing = 60
    
    def boundingRect(self) -> QRectF:
        """Определение границ элемента"""
        padding = 10
        return QRectF(
            -padding, -padding,
            self.width + 2 * padding,
            self.height + 2 * padding
        )
    
    def paint(self, painter: QPainter, option, widget=None):
        """Отрисовка элемента"""
        # Фон зоны
        painter.setBrush(QBrush(self.color.lighter(130)))
        painter.setPen(QPen(self.color.darker(150), 2))
        
        # Скругленный прямоугольник
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width, self.height, 10, 10)
        painter.drawPath(path)
        
        # Заголовок зоны
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.drawText(10, 25, self.zone.name)
        
        # Подзаголовок (тип зоны и количество устройств)
        subtitle = f"{self.zone.zone_type.value} • {len(self.device_items)} устройств"
        painter.setFont(QFont("Arial", 9))
        painter.drawText(10, 45, subtitle)
    
    def add_device(self, device: NetworkDevice) -> DeviceItem:
        """Добавить устройство в зону"""
        device_item = DeviceItem(device)
        
        # Рассчитываем позицию устройства
        row = len(self.device_items) // 4
        col = len(self.device_items) % 4
        x = 20 + col * self.device_spacing
        y = 70 + row * self.device_spacing
        
        device_item.setPos(x, y)
        self.device_items.append(device_item)
        
        # Добавляем на сцену
        scene = self.scene()
        if scene:
            scene.addItem(device_item)
            device_item.setParentItem(self)
        
        self.device_added.emit(device)
        return device_item
    
    def remove_device_item(self, device_item: DeviceItem):
        """Удалить устройство из зоны"""
        if device_item in self.device_items:
            self.device_items.remove(device_item)
            scene = self.scene()
            if scene:
                scene.removeItem(device_item)
            self.device_removed.emit(device_item.device)
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Обработка двойного клика по зоне"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.edit_zone_properties()
    
    def contextMenuEvent(self, event):
        """Показать контекстное меню зоны"""
        menu = QMenu()
        
        edit_action = menu.addAction("✏️ Редактировать")
        menu.addSeparator()
        color_action = menu.addAction("🎨 Изменить цвет")
        menu.addSeparator()
        remove_action = menu.addAction("🗑️ Удалить зону")
        
        action = menu.exec(event.screenPos())
        
        if action == edit_action:
            self.edit_zone_properties()
        elif action == color_action:
            self.change_color()
        elif action == remove_action:
            self.remove_zone()
    
    def edit_zone_properties(self):
        """Редактировать свойства зоны"""
        # Здесь будет вызов диалога редактирования
        print(f"Редактирую зону {self.zone.name}")
    
    def change_color(self):
        """Изменить цвет зоны"""
        from PyQt6.QtWidgets import QColorDialog
        
        color = QColorDialog.getColor(self.color, None, "Выберите цвет зоны")
        if color.isValid():
            self.color = color
            self.zone.color = color.name()
            self.update()
    
    def remove_zone(self):
        """Удалить зону"""
        scene = self.scene()
        if scene:
            scene.removeItem(self)
