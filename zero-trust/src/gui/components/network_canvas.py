"""
Холст для визуализации сети
"""

from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PyQt6.QtCore import Qt, QRect, QPoint

from ....core.models import NetworkPolicy, SecurityZone, NetworkDevice

class NetworkCanvas(QWidget):
    """Холст для визуализации сетевой топологии"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.policy = None
        self.selected_zone = None
        self.setup_ui()
    
    def setup_ui(self):
        """Настроить холст"""
        self.setMinimumSize(600, 400)
        self.setStyleSheet("background-color: white;")
    
    def set_policy(self, policy: NetworkPolicy):
        """Установить политику для отображения"""
        self.policy = policy
        self.update()
    
    def paintEvent(self, event):
        """Отрисовка сети"""
        if not self.policy:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Очищаем фон
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        # Рисуем зоны
        zones = list(self.policy.zones.values())
        zone_rects = []
        
        for i, zone in enumerate(zones):
            # Позиция зоны
            x = 50 + (i % 3) * 200
            y = 50 + (i // 3) * 150
            
            # Цвет зоны
            color = self._get_zone_color(zone.zone_type.value)
            
            # Рисуем прямоугольник зоны
            painter.setBrush(QBrush(color, Qt.BrushStyle.SolidPattern))
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            rect = QRect(x, y, 180, 120)
            painter.drawRoundedRect(rect, 10, 10)
            
            # Название зоны
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.drawText(rect, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, 
                           zone.name)
            
            # Количество устройств
            device_text = f"Устройств: {zone.device_count}"
            painter.setFont(QFont("Arial", 8))
            painter.drawText(rect, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
                           device_text)
            
            zone_rects.append((zone, rect))
        
        # Рисуем соединения между зонами (правила)
        painter.setPen(QPen(QColor(100, 100, 100), 1, Qt.PenStyle.DashLine))
        
        for rule in self.policy.rules:
            src_index = zones.index(rule.source_zone)
            dst_index = zones.index(rule.destination_zone)
            
            if src_index < len(zone_rects) and dst_index < len(zone_rects):
                src_rect = zone_rects[src_index][1]
                dst_rect = zone_rects[dst_index][1]
                
                # Центры прямоугольников
                src_center = src_rect.center()
                dst_center = dst_rect.center()
                
                # Цвет линии в зависимости от действия
                if rule.action.value == 'allow':
                    painter.setPen(QPen(QColor(40, 167, 69), 2))  # Зеленый
                else:
                    painter.setPen(QPen(QColor(220, 53, 69), 2))  # Красный
                
                # Рисуем линию
                painter.drawLine(src_center, dst_center)
                
                # Стрелка
                self._draw_arrow(painter, src_center, dst_center)
    
    def _get_zone_color(self, zone_type: str) -> QColor:
        """Получить цвет для типа зоны"""
        colors = {
            "trusted": QColor(76, 175, 80),
            "dmz": QColor(255, 193, 7),
            "iot": QColor(156, 39, 176),
            "guest": QColor(33, 150, 243),
            "server": QColor(244, 67, 54),
            "custom": QColor(158, 158, 158)
        }
        return colors.get(zone_type, QColor(200, 200, 200))
    
    def _draw_arrow(self, painter: QPainter, start: QPoint, end: QPoint):
        """Нарисовать стрелку"""
        import math
        
        # Длина стрелки
        arrow_length = 10
        
        # Угол линии
        angle = math.atan2(end.y() - start.y(), end.x() - start.x())
        
        # Координаты стрелки
        x1 = end.x() - arrow_length * math.cos(angle - math.pi/6)
        y1 = end.y() - arrow_length * math.sin(angle - math.pi/6)
        x2 = end.x() - arrow_length * math.cos(angle + math.pi/6)
        y2 = end.y() - arrow_length * math.sin(angle + math.pi/6)
        
        # Рисуем стрелку
        painter.drawLine(end, QPoint(int(x1), int(y1)))
        painter.drawLine(end, QPoint(int(x2), int(y2)))
