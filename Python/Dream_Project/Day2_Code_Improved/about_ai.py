from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt

def build_about_page():
    page = QWidget()
    page.setStyleSheet("background: transparent; border: none;")
    lay = QVBoxLayout(page)
    lay.setContentsMargins(0, 10, 0, 0)
    lay.setSpacing(0)

    heading = QLabel("✨ ABOUT AI ✨")
    heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
    heading.setStyleSheet("color: #27c93f; font-size: 18px; font-weight: 800; letter-spacing: 2px; border: none; margin-bottom: 20px; background: transparent;")
    lay.addWidget(heading)

    container = QFrame()
    container.setStyleSheet("background: transparent; border: none;")
    container_layout = QVBoxLayout(container)
    container_layout.setContentsMargins(10, 0, 10, 0)
    container_layout.setSpacing(0)

    items = [
        ("FOUNDER", "Alven Alex [Pradeep Kumar Gupta]"),
        ("LANGUAGE", "Python"),
        ("UI STYLE", "Glassmorphism / Modern"),
        ("FEATURES", "• Turbo Mode\n• Ghost Mode\n• Safe Mode"),
        ("VERSION", "2.0.0")
    ]
    
    for title, value in items:
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #27c93f; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; border: none; margin-bottom: 6px; background: transparent;")
        container_layout.addWidget(title_lbl)
        value_lbl = QLabel(value)
        value_lbl.setStyleSheet("color: white; font-size: 14px; font-weight: 500; border: none; margin-bottom: 15px; background: transparent;")
        container_layout.addWidget(value_lbl)

    lay.addWidget(container)
    lay.addStretch()

    quote = QLabel("“Unlock More Features With Alvens OS”")
    quote.setAlignment(Qt.AlignmentFlag.AlignCenter)
    quote.setStyleSheet("color: rgba(39, 201, 63, 0.6); font-size: 9px; font-style: italic; border: none; margin-top: 10px; background: transparent;")
    lay.addWidget(quote)

    return page