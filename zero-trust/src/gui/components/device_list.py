"""
Виджет списка устройств
"""

from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import Qt

from ....core.models import NetworkDevice, DeviceType

class DeviceListWidget(QListWidget):
    """Виджет для отображения списка устройств"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Настроить внешний вид"""
        self.setIconSize(24, 24)
        self.setSortingEnabled(True)
    
    def add_device(self, device: NetworkDevice):
        """Добавить устройство в список"""
        item = QListWidgetItem()
        
        # Текст элемента
        display_text = device.hostname or device.ip_address
        if device.device_type != DeviceType.UNKNOWN:
            display_text += f" ({device.device_type.value})"
        
        item.setText(display_text)
        
        # Иконка в зависимости от типа
        icon_name = self._get_icon_for_device(device)
        if icon_name:
            item.setIcon(QIcon(icon_name))
        
        # Цвет в зависимости от уровня риска
        if device.risk_score > 0.7:
            item.setForeground(QColor(220, 53, 69))  # Красный
        elif device.risk_score > 0.4:
            item.setForeground(QColor(255, 193, 7))  # Желтый
        
        # Сохраняем данные устройства
        item.setData(Qt.ItemDataRole.UserRole, device)
        
        self.addItem(item)
    
    def _get_icon_for_device(self, device: NetworkDevice) -> str:
        """Получить путь к иконке для устройства"""
        icon_map = {
            DeviceType.ROUTER: "assets/icons/router.svg",
            DeviceType.COMPUTER: "assets/icons/computer.svg",
            DeviceType.PHONE: "assets/icons/phone.svg",
            DeviceType.IOT: "assets/icons/iot.svg",
            DeviceType.PRINTER: "assets/icons/printer.svg",
            DeviceType.CAMERA: "assets/icons/camera.svg",
            DeviceType.SERVER: "assets/icons/server.svg",
        }
        return icon_map.get(device.device_type, "assets/icons/unknown.svg")
    
    def get_selected_device(self) -> NetworkDevice:
        """Получить выбранное устройство"""
        selected_items = self.selectedItems()
        if selected_items:
            return selected_items[0].data(Qt.ItemDataRole.UserRole)
        return None
    
    def clear_devices(self):
        """Очистить список устройств"""
        self.clear()
