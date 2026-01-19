"""
Страница "Конструктор политик"
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ConstructorPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("🎨 Конструктор политик (в разработке)"))
        self.setLayout(layout)
