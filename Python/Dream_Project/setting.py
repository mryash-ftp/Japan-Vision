from PyQt6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QSlider
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication
import os, platform

# Toggle Switch
class ToggleSwitch(QPushButton):
    toggledAnimated = pyqtSignal(bool)
    def __init__(self, initial=False, on_text="ON", off_text="OFF", parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(initial)
        self.on_text = on_text
        self.off_text = off_text
        self.setFixedSize(58, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self._emit_toggled)
        self.refresh()
    def _emit_toggled(self):
        self.refresh()
        self.toggledAnimated.emit(self.isChecked())
    def refresh(self):
        if self.isChecked():
            self.setText(self.on_text)
            self.setStyleSheet("""QPushButton { background: #00d4ff; color: white; border: none; border-radius: 14px; font-weight: 700; font-size: 10px; }""")
        else:
            self.setText(self.off_text)
            self.setStyleSheet("""QPushButton { background: rgba(255,255,255,0.12); color: rgba(255,255,255,0.9); border: none; border-radius: 14px; font-weight: 700; font-size: 10px; }""")

def build_preferences_page(parent):
    page = QWidget()
    page.setStyleSheet("background: transparent; border: none;")
    lay = QVBoxLayout(page)
    lay.setContentsMargins(0, 10, 0, 0)
    lay.setSpacing(14)

    heading = QLabel("⚙️ PREFERENCES")
    heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
    heading.setStyleSheet("color: #ffbd2e; font-size: 17px; font-weight: 800; letter-spacing: 1px; border: none; background: transparent;")
    lay.addWidget(heading)

    pc_name = os.environ.get("USERNAME") or platform.node() or "USER"
    welcome_card = QFrame()
    welcome_card.setStyleSheet("background: rgba(255,255,255,0.04); border-radius: 12px; border: none;")
    welcome_layout = QHBoxLayout(welcome_card)
    welcome_layout.setContentsMargins(15, 10, 15, 10)
    welcome_icon = QLabel("👋")
    welcome_icon.setStyleSheet("font-size: 16px; border: none; background: transparent;")
    welcome_text = QLabel(f"Welcome, {pc_name}")
    welcome_text.setStyleSheet("color: white; font-size: 13px; font-weight: 600; border: none; background: transparent;")
    welcome_layout.addWidget(welcome_icon)
    welcome_layout.addWidget(welcome_text)
    welcome_layout.addStretch()
    lay.addWidget(welcome_card)

    section = QLabel("⚡ SYSTEM PREFERENCES")
    section.setStyleSheet("color: #ffbd2e; font-size: 12px; font-weight: 700; letter-spacing: 0.5px; margin-top: 4px; background: transparent;")
    lay.addWidget(section)

    prefs = [("🔄", "AUTO START", False), ("♦", "FLOT ICON", True), ("🔶", "AI Assistant", True)]
    for icon, name, initial in prefs:
        card = QFrame()
        card.setStyleSheet("QFrame { background: rgba(255,255,255,0.04); border-radius: 12px; border: none; }")
        card_lay = QHBoxLayout(card)
        card_lay.setContentsMargins(14, 10, 14, 10)
        lbl = QLabel(f"{icon} {name}")
        lbl.setStyleSheet("color: white; font-size: 13px; font-weight: 600; border: none; background: transparent;")
        toggle = ToggleSwitch(initial)

        def _on_toggle(checked, n=name):
            from main import show_toast
            if n == "FLOT ICON":
                parent.float_icon_enabled = checked
            if checked:
                show_toast(f"{n} enabled successfully", success=True)
            else:
                show_toast(f"{n} disabled successfully", success=False)

        toggle.toggledAnimated.connect(_on_toggle)
        card_lay.addWidget(lbl)
        card_lay.addStretch()
        card_lay.addWidget(toggle)
        lay.addWidget(card)

    # AI SENSITIVITY LEVEL (changed from PERFORMANCE LEVEL)
    sensitivity_label = QLabel("🎤 AI Voice ")
    sensitivity_label.setStyleSheet("color: #ffbd2e; font-size: 12px; font-weight: 700; letter-spacing: 0.5px; margin-top: 4px; background: transparent;")
    lay.addWidget(sensitivity_label)

    slider_card = QFrame()
    slider_card.setStyleSheet("background: rgba(255,255,255,0.04); border-radius: 12px; border: none;")
    slider_lay = QVBoxLayout(slider_card)
    slider_lay.setContentsMargins(16, 12, 16, 10)
    slider_lay.setSpacing(6)

    parent.ai_slider = QSlider(Qt.Orientation.Horizontal)
    parent.ai_slider.setRange(0, 100)
    parent.ai_slider.setValue(65)
    parent.ai_slider.setCursor(Qt.CursorShape.PointingHandCursor)
    parent.ai_slider.valueChanged.connect(parent.on_ai_level_changed)
    parent.ai_slider.setStyleSheet("""
        QSlider::groove:horizontal { height: 3px; background: rgba(255,255,255,0.15); border-radius: 1.5px; }
        QSlider::sub-page:horizontal { background: #ffbd2e; border-radius: 1.5px; }
        QSlider::handle:horizontal { background: #ffbd2e; width: 12px; height: 12px; margin: -4.5px 0; border-radius: 6px; }
        QSlider::handle:horizontal:hover { background: #ffd15a; }
    """)
    slider_lay.addWidget(parent.ai_slider)

    # Removed Low/Mid/High labels - sirf slider hai ab

    lay.addWidget(slider_card)
    lay.addStretch()
    return page