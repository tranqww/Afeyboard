"""Dark-mode QSS theme for Afeyboard. Neon-violet accent, rounded, minimal."""

BG = "#0f1115"
PANEL = "#171a21"
SIDEBAR = "#12141a"
ELEVATED = "#1c2029"
BORDER = "#272c37"
TEXT = "#e7e9f0"
TEXT_MUTED = "#9099a8"
ACCENT = "#8b5cf6"
ACCENT_HOVER = "#a78bfa"
ACCENT_PRESSED = "#7c3aed"
ACCENT_CYAN = "#22d3ee"
DANGER = "#ef4444"
DANGER_HOVER = "#f87171"

STYLESHEET = f"""
* {{
    font-family: "Segoe UI", "Segoe UI Semibold", sans-serif;
    color: {TEXT};
    outline: none;
}}

QWidget#Root, QMainWindow {{
    background-color: {BG};
}}

QWidget#Sidebar {{
    background-color: {SIDEBAR};
    border-right: 1px solid {BORDER};
}}

QLabel#LogoLabel {{
    color: {TEXT};
    font-size: 18px;
    font-weight: 600;
    padding: 22px 20px 4px 20px;
}}

QLabel#LogoSubLabel {{
    color: {TEXT_MUTED};
    font-size: 11px;
    padding: 0px 20px 18px 20px;
    letter-spacing: 1px;
}}

QPushButton#NavButton {{
    background-color: transparent;
    border: none;
    border-left: 3px solid transparent;
    border-radius: 0px;
    text-align: left;
    padding: 13px 20px;
    font-size: 13px;
    color: {TEXT_MUTED};
}}

QPushButton#NavButton:hover {{
    background-color: {ELEVATED};
    color: {TEXT};
}}

QPushButton#NavButton:checked {{
    background-color: {ELEVATED};
    color: {TEXT};
    border-left: 3px solid {ACCENT};
    font-weight: 600;
}}

QWidget#PageHeader QLabel#PageTitle {{
    font-size: 20px;
    font-weight: 600;
    color: {TEXT};
}}

QWidget#PageHeader QLabel#PageSubtitle {{
    font-size: 12px;
    color: {TEXT_MUTED};
}}

QGroupBox {{
    background-color: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 10px;
    margin-top: 14px;
    padding: 14px 14px 12px 14px;
    font-weight: 600;
    font-size: 12px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: {ACCENT_HOVER};
}}

QLabel {{
    background: transparent;
    font-size: 12px;
}}

QLineEdit, QPlainTextEdit, QTextEdit {{
    background-color: {ELEVATED};
    border: 1px solid {BORDER};
    border-radius: 7px;
    padding: 7px 10px;
    font-size: 12px;
    selection-background-color: {ACCENT};
}}

QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus {{
    border: 1px solid {ACCENT};
}}

QLineEdit:disabled, QPlainTextEdit:disabled {{
    color: {TEXT_MUTED};
    background-color: #161920;
}}

QSpinBox, QDoubleSpinBox {{
    background-color: {ELEVATED};
    border: 1px solid {BORDER};
    border-radius: 7px;
    padding: 6px 8px;
    font-size: 12px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1px solid {ACCENT};
}}

QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    width: 16px;
    border: none;
    background: transparent;
}}

QComboBox {{
    background-color: {ELEVATED};
    border: 1px solid {BORDER};
    border-radius: 7px;
    padding: 6px 10px;
    font-size: 12px;
    min-height: 20px;
}}

QComboBox:focus {{
    border: 1px solid {ACCENT};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox::down-arrow {{
    image: none;
    width: 0;
    height: 0;
    border-left: 3px solid transparent;
    border-right: 3px solid transparent;
    border-top: 4px solid {TEXT_MUTED};
    margin-right: 6px;
}}

QComboBox QAbstractItemView {{
    background-color: {ELEVATED};
    border: 1px solid {BORDER};
    selection-background-color: {ACCENT};
    outline: none;
    padding: 4px;
    border-radius: 6px;
}}

QPushButton {{
    background-color: {ELEVATED};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: #242936;
    border: 1px solid {ACCENT};
}}

QPushButton:pressed {{
    background-color: #1a1e27;
}}

QPushButton:disabled {{
    color: {TEXT_MUTED};
    background-color: {PANEL};
    border: 1px solid {BORDER};
}}

QPushButton#PrimaryButton {{
    background-color: {ACCENT};
    border: 1px solid {ACCENT};
    color: white;
}}

QPushButton#PrimaryButton:hover {{
    background-color: {ACCENT_HOVER};
    border: 1px solid {ACCENT_HOVER};
}}

QPushButton#PrimaryButton:pressed {{
    background-color: {ACCENT_PRESSED};
}}

QPushButton#PrimaryButton:disabled {{
    background-color: {ELEVATED};
    color: {TEXT_MUTED};
    border: 1px solid {BORDER};
}}

QPushButton#DangerButton {{
    background-color: transparent;
    border: 1px solid {DANGER};
    color: {DANGER};
}}

QPushButton#DangerButton:hover {{
    background-color: {DANGER};
    color: white;
}}

QPushButton#DangerButton:disabled {{
    border: 1px solid {BORDER};
    color: {TEXT_MUTED};
}}

QCheckBox, QRadioButton {{
    font-size: 12px;
    spacing: 8px;
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {BORDER};
    background-color: {ELEVATED};
}}

QCheckBox::indicator {{
    border-radius: 4px;
}}

QRadioButton::indicator {{
    border-radius: 8px;
}}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background-color: {ACCENT};
    border: 1px solid {ACCENT};
}}

QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
    border: 1px solid {ACCENT_HOVER};
}}

QTableWidget {{
    background-color: {ELEVATED};
    border: 1px solid {BORDER};
    border-radius: 8px;
    gridline-color: {BORDER};
    font-size: 12px;
}}

QHeaderView::section {{
    background-color: {PANEL};
    color: {TEXT_MUTED};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 6px;
    font-weight: 600;
}}

QTableWidget::item:selected {{
    background-color: {ACCENT};
    color: white;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 5px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: {ACCENT};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
}}

QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 5px;
    min-width: 24px;
}}

QStatusBar {{
    background-color: {SIDEBAR};
    border-top: 1px solid {BORDER};
    color: {TEXT_MUTED};
    font-size: 11px;
}}

QStatusBar::item {{
    border: none;
}}

QSplitter::handle {{
    background-color: {BORDER};
}}

QToolTip {{
    background-color: {ELEVATED};
    color: {TEXT};
    border: 1px solid {ACCENT};
    padding: 4px 8px;
    border-radius: 6px;
}}
"""
