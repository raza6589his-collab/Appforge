"""
Enterprise Minimalist Theme for AppForge Studio
Inspired by Tier-1 developer tools (GitHub Desktop, VS Code, Linear)
"""

MAIN_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: 'Segoe UI', 'Tahoma', -apple-system, sans-serif;
    font-size: 12px;
}

/* Section Headings */
QLabel#SectionTitle {
    font-size: 13px;
    font-weight: 600;
    color: #f0f6fc;
    padding-bottom: 4px;
    border-bottom: 1px solid #21262d;
    margin-bottom: 6px;
}

QLabel {
    color: #8b949e;
}

/* Text Inputs & Comboboxes */
QLineEdit, QComboBox {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 7px 10px;
    color: #f0f6fc;
    font-size: 12px;
    selection-background-color: #1f6feb;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #58a6ff;
    background-color: #0d1117;
}

QLineEdit:disabled, QComboBox:disabled {
    background-color: #21262d;
    color: #484f58;
}

/* Buttons */
QPushButton {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 14px;
    color: #c9d1d9;
    font-weight: 500;
    font-size: 12px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #30363d;
    border-color: #8b949e;
    color: #f0f6fc;
}

QPushButton:pressed {
    background-color: #161b22;
}

QPushButton:disabled {
    background-color: #161b22;
    border-color: #21262d;
    color: #484f58;
}

QPushButton#PrimaryButton {
    background-color: #238636;
    border: 1px solid #2ea043;
    border-radius: 6px;
    color: #ffffff;
    font-size: 13px;
    font-weight: 600;
    padding: 10px 16px;
}

QPushButton#PrimaryButton:hover {
    background-color: #2ea043;
    border-color: #3fb950;
}

QPushButton#PrimaryButton:disabled {
    background-color: #21262d;
    border-color: #30363d;
    color: #484f58;
}

QPushButton#DangerButton {
    background-color: #21262d;
    border: 1px solid #da3633;
    border-radius: 6px;
    color: #f85149;
    padding: 6px 12px;
}

QPushButton#DangerButton:hover {
    background-color: #b62324;
    color: #ffffff;
}

QPushButton#DangerButton:disabled {
    border-color: #30363d;
    color: #484f58;
    background-color: #161b22;
}

QPushButton#SuccessButton {
    background-color: #21262d;
    border: 1px solid #238636;
    border-radius: 6px;
    color: #3fb950;
    padding: 6px 12px;
}

QPushButton#SuccessButton:hover {
    background-color: #238636;
    color: #ffffff;
}

QPushButton#SuccessButton:disabled {
    border-color: #30363d;
    color: #484f58;
    background-color: #161b22;
}

/* Checkboxes */
QCheckBox {
    color: #c9d1d9;
    spacing: 8px;
    font-size: 12px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #30363d;
    border-radius: 4px;
    background-color: #161b22;
}

QCheckBox::indicator:hover {
    border-color: #58a6ff;
}

QCheckBox::indicator:checked {
    background-color: #1f6feb;
    border-color: #58a6ff;
}

/* ProgressBar */
QProgressBar {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 4px;
    text-align: center;
    color: #8b949e;
    font-size: 11px;
    height: 6px;
}

QProgressBar::chunk {
    background-color: #238636;
    border-radius: 3px;
}

/* Terminal & Logs */
QTextEdit#TerminalLogs {
    background-color: #06090f;
    border: 1px solid #21262d;
    border-radius: 6px;
    color: #c9d1d9;
    font-family: 'Consolas', 'Cascadia Code', monospace;
    font-size: 12px;
    padding: 8px;
}

QScrollBar:vertical {
    background-color: #0d1117;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #21262d;
    border-radius: 4px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background-color: #30363d;
}

/* Bottom Status Bar */
QFrame#FooterStatusBar {
    background-color: #161b22;
    border-top: 1px solid #21262d;
    padding: 4px 16px;
}
"""
