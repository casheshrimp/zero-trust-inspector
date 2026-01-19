"""
Стили и темы приложения
"""
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import Qt

class AppStyles:
    """Стили приложения ZeroTrust Inspector"""
    
    # Цветовая схема (темная тема с синим акцентом)
    COLORS = {
        'primary': '#0B5394',      # Основной синий
        'primary_dark': '#073763',
        'primary_light': '#3D85C6',
        
        'secondary': '#6FA8DC',
        'accent': '#FF9900',
        'danger': '#E06666',
        'warning': '#FFD966',
        'success': '#93C47D',
        'info': '#76A5AF',
        
        'background': '#1E1E1E',
        'surface': '#252525',
        'surface_light': '#2D2D2D',
        'text': '#FFFFFF',
        'text_secondary': '#B0B0B0',
        'border': '#404040',
        
        # Цвета зон безопасности
        'zone_trusted': '#90EE90',
        'zone_iot': '#FFFF99',
        'zone_guest': '#D3D3D3',
        'zone_server': '#ADD8E6',
        'zone_dmz': '#FFB6C1',
        'zone_custom': '#E6E6FA',
    }
    
    # Шрифты
    FONTS = {
        'title': QFont("Segoe UI", 22, QFont.Weight.Bold),
        'heading': QFont("Segoe UI", 17, QFont.Weight.DemiBold),
        'subheading': QFont("Segoe UI", 14, QFont.Weight.Medium),
        'body': QFont("Segoe UI", 12),
        'caption': QFont("Segoe UI", 11),
        'monospace': QFont("Consolas", 12),
    }
    
    @staticmethod
    def create_dark_palette():
        """Создать темную палитру"""
        palette = QPalette()
        
        # Основные цвета
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(37, 37, 37))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(59, 59, 59))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        
        # Текст
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(128, 128, 128))
        
        # Кнопки
        palette.setColor(QPalette.ColorRole.Button, QColor(59, 59, 59))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        
        # Ссылки и выделение
        palette.setColor(QPalette.ColorRole.Link, QColor(109, 168, 220))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(11, 83, 148))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        return palette
    
    @staticmethod
    def get_stylesheet():
        """Получить CSS стили для приложения"""
        colors = AppStyles.COLORS
        
        return f"""
        /* Основные стили */
        QMainWindow {{
            background-color: {colors['background']};
        }}
        
        QWidget {{
            color: {colors['text']};
            background-color: {colors['background']};
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        
        /* Кнопки */
        QPushButton {{
            background-color: {colors['primary']};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: 500;
        }}
        
        QPushButton:hover {{
            background-color: {colors['primary_light']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['primary_dark']};
        }}
        
        QPushButton:disabled {{
            background-color: {colors['surface']};
            color: {colors['text_secondary']};
        }}
        
        /* Текстовые поля */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 6px;
            selection-background-color: {colors['primary']};
        }}
        
        /* Выпадающие списки */
        QComboBox {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 6px;
            min-width: 100px;
        }}
        
        QComboBox::drop-down {{
            border: none;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {colors['text']};
        }}
        
        /* Чекбоксы и радиокнопки */
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {colors['border']};
            border-radius: 3px;
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {colors['primary']};
            border-color: {colors['primary']};
            image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12"><path fill="white" d="M10.3 3.3L5 8.6 1.7 5.3c-.4-.4-1-.4-1.4 0-.4.4-.4 1 0 1.4l4 4c.2.2.4.3.7.3.3 0 .5-.1.7-.3l6-6c.4-.4.4-1 0-1.4-.4-.4-1-.4-1.4 0z"/></svg>');
        }}
        
        /* Списки и таблицы */
        QListWidget, QTreeWidget, QTableView {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            alternate-background-color: {colors['surface_light']};
        }}
        
        QListWidget::item, QTreeWidget::item {{
            padding: 6px;
            border-bottom: 1px solid {colors['border']};
        }}
        
        QListWidget::item:selected, QTreeWidget::item:selected {{
            background-color: {colors['primary']};
            color: white;
        }}
        
        /* Вкладки */
        QTabWidget::pane {{
            border: 1px solid {colors['border']};
            border-radius: 4px;
            background-color: {colors['surface']};
        }}
        
        QTabBar::tab {{
            background-color: {colors['surface']};
            color: {colors['text_secondary']};
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['primary']};
            color: white;
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {colors['surface_light']};
        }}
        
        /* Прогресс-бар */
        QProgressBar {{
            border: 1px solid {colors['border']};
            border-radius: 4px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['primary']};
            border-radius: 4px;
        }}
        
        /* Групповые рамки */
        QGroupBox {{
            font-weight: bold;
            border: 1px solid {colors['border']};
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 12px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            background-color: {colors['surface']};
        }}
        
        /* Сплиттеры */
        QSplitter::handle {{
            background-color: {colors['border']};
        }}
        
        QSplitter::handle:hover {{
            background-color: {colors['primary']};
        }}
        
        /* Скроллбары */
        QScrollBar:vertical {{
            background-color: {colors['surface']};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors['border']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors['text_secondary']};
        }}
        
        /* Статус бар */
        QStatusBar {{
            background-color: {colors['surface']};
            color: {colors['text_secondary']};
            border-top: 1px solid {colors['border']};
        }}
        
        /* Меню */
        QMenuBar {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border-bottom: 1px solid {colors['border']};
        }}
        
        QMenu {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
        }}
        
        QMenu::item {{
            padding: 6px 24px 6px 12px;
        }}
        
        QMenu::item:selected {{
            background-color: {colors['primary']};
        }}
        
        /* Кастомные классы */
        .TitleLabel {{
            font-size: 18px;
            font-weight: bold;
            color: {colors['primary']};
        }}
        
        .HeadingLabel {{
            font-size: 14px;
            font-weight: 600;
            color: {colors['text']};
        }}
        
        .Card {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 16px;
        }}
        
        .DeviceCard {{
            background-color: {colors['surface_light']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 12px;
            margin: 4px 0;
        }}
        
        .ZoneCard {{
            border-radius: 8px;
            padding: 12px;
            margin: 8px;
        }}
        
        .ZoneTrusted {{
            background-color: {colors['zone_trusted']}20;
            border: 2px solid {colors['zone_trusted']};
            color: #1a531b;
        }}
        
        .ZoneIOT {{
            background-color: {colors['zone_iot']}20;
            border: 2px solid {colors['zone_iot']};
            color: #8a6d00;
        }}
        
        .ZoneGuest {{
            background-color: {colors['zone_guest']}20;
            border: 2px solid {colors['zone_guest']};
            color: #5a5a5a;
        }}
        
        .SuccessLabel {{
            color: {colors['success']};
            font-weight: bold;
        }}
        
        .WarningLabel {{
            color: {colors['warning']};
            font-weight: bold;
        }}
        
        .ErrorLabel {{
            color: {colors['danger']};
            font-weight: bold;
        }}
        
        .InfoLabel {{
            color: {colors['info']};
            font-weight: bold;
        }}
        """
