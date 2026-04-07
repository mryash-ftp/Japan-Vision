from PyQt6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QLinearGradient, QFont

# Circular Progress
class CircularProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0
        self.target = 0
        self.setFixedSize(130, 130)
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(20)

    def set_progress(self, value):
        self.target = max(0, min(100, value))

    def animate(self):
        if self.progress < self.target:
            self.progress += 2
            if self.progress > self.target:
                self.progress = self.target
            self.update()
        elif self.progress > self.target:
            self.progress -= 2
            if self.progress < self.target:
                self.progress = self.target
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QPen(QColor(255, 255, 255, 20), 6))
        p.drawEllipse(15, 15, 100, 100)
        grad = QLinearGradient(0, 0, 130, 130)
        grad.setColorAt(0, QColor("#00d4ff"))
        grad.setColorAt(1, QColor("#27c93f"))
        p.setPen(QPen(QBrush(grad), 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        angle = int(360 * self.progress / 100)
        if angle > 0:
            p.drawArc(15, 15, 100, 100, 90 * 16, -angle * 16)
        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{self.progress}%")

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

def build_dashboard_page(parent):
    page = QWidget()
    page.setStyleSheet("background: transparent; border: none;")
    lay = QVBoxLayout(page)
    lay.setContentsMargins(0, 10, 0, 0)
    lay.setSpacing(16)

    heading = QLabel("⚡ DASHBOARD")
    heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
    heading.setStyleSheet("color: #00d4ff; font-size: 17px; font-weight: 800; letter-spacing: 1px; border: none; background: transparent;")
    lay.addWidget(heading)

    parent.progress_ring = CircularProgress()
    lay.addWidget(parent.progress_ring, alignment=Qt.AlignmentFlag.AlignCenter)

    toggles = [("🚀", "AI TURBO"), ("👻", "GHOST MODE"), ("🛡️", "SAFE MODE")]
    for icon, name in toggles:
        card = QFrame()
        card.setStyleSheet("QFrame { background: rgba(255,255,255,0.04); border-radius: 12px; border: none; }")
        card_lay = QHBoxLayout(card)
        card_lay.setContentsMargins(14, 10, 14, 10)
        lbl = QLabel(f"{icon} {name}")
        lbl.setStyleSheet("color: white; font-size: 13px; font-weight: 600; border: none; background: transparent;")
        toggle = ToggleSwitch(False)
        toggle.toggledAnimated.connect(lambda checked, n=name: parent.handle_dashboard_toggle(n, checked))
        card_lay.addWidget(lbl)
        card_lay.addStretch()
        card_lay.addWidget(toggle)
        lay.addWidget(card)

    lay.addStretch()
    return page