"""
Графический элемент устройства для отображения на холсте
"""

from PyQt6.QtWidgets import QGraphicsItem, QMenu
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import (
    QPainter, QBrush, QPen, QColor, QFont,
    QPainterPath, QMouseEvent
)

from ...core.models import NetworkDevice, DeviceType
from ...core.constants import DEVICE_ICONS

class DeviceItem(QGraphicsItem):
    """Графический элемент для отображения устройства"""
    
    def __init__(self, device: NetworkDevice, parent=None):
        super().__init__(parent)
        self.device = device
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        
        self.hovered = False
        self.selected_color = QColor(255, 215, 0)  # Золотой для выделения
    
    def boundingRect(self) -> QRectF:
        """Определение границ элемента"""
        return QRectF(0, 0, 40, 40)
    
    def paint(self, painter: QPainter, option, widget=None):
        """Отрисовка элемента"""
        # Фон
        if self.isSelected():
            painter.setBrush(QBrush(self.selected_color))
        elif self.hovered:
            painter.setBrush(QBrush(QColor(200, 230, 255)))  # Светло-голубой при наведении
        else:
            painter.setBrush(QBrush(QColor(240, 240, 240)))  # Светло-серый
        
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        
        # Скругленный прямоугольник
        path = QPainterPath()
        path.addRoundedRect(0, 0, 40, 40, 10, 10)
        painter.drawPath(path)
        
        # Иконка устройства
        icon_char = DEVICE_ICONS.get(self.device.device_type.value, "❓")
        painter.setFont(QFont("Arial", 20))
        painter.drawText(10, 30, icon_char)
        
        # IP адрес (короткий)
        short_ip = self.device.ip_address.split('.')[-1]
        painter.setFont(QFont("Arial", 8))
        painter.drawText(5, 15, f".{short_ip}")
    
    def mousePressEvent(self, event: QMouseEvent):
        """Обработка нажатия мыши"""
        if event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event)
        else:
            super().mousePressEvent(event)
    
    def hoverEnterEvent(self, event):
        """Обработка входа курсора"""
        self.hovered = True
        self.update()
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Обработка выхода курсора"""
        self.hovered = False
        self.update()
        super().hoverLeaveEvent(event)
    
    def show_context_menu(self, event):
        """Показать контекстное меню устройства"""
        menu = QMenu()
        
        info_action = menu.addAction("📋 Информация")
        menu.addSeparator()
        remove_action = menu.addAction("🗑️ Удалить из зоны")
        
        action = menu.exec(event.screenPos())
        
        if action == info_action:
            self.show_device_info()
        elif action == remove_action:
            self.remove_from_zone()
    
    def show_device_info(self):
        """Показать информацию об устройстве"""
        # Здесь будет вызов диалога с информацией
        print(f"Показываю информацию об устройстве {self.device.ip_address}")
    
    def remove_from_zone(self):
        """Удалить устройство из зоны"""
        parent = self.parentItem()
        if parent and hasattr(parent, 'remove_device_item'):
            parent.remove_device_item(self)
            # Здесь нужно вернуть устройство в список доступных
