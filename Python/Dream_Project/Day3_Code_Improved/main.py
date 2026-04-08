import sys
import os
import ctypes
import platform

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame,
    QLabel, QStackedWidget, QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt6.QtGui import (
    QPainter, QColor, QBrush, QPen, QFont, QIcon, QAction, QPixmap
)

# Import pages
from dashboard import build_dashboard_page
from setting import build_preferences_page
from about_ai import build_about_page
from ai_mode import build_ai_mode_page
from ai_agent import AIAgent

# =========================================================
# WINDOWS BLUR
# =========================================================
def set_blur(hwnd):
    try:
        class ACCENT_POLICY(ctypes.Structure):
            _fields_ = [("AccentState", ctypes.c_int), ("AccentFlags", ctypes.c_int), ("GradientColor", ctypes.c_int), ("AnimationId", ctypes.c_int)]
        class DATA(ctypes.Structure):
            _fields_ = [("Attribute", ctypes.c_int), ("Data", ctypes.POINTER(ACCENT_POLICY)), ("SizeOfData", ctypes.c_size_t)]
        accent = ACCENT_POLICY()
        accent.AccentState = 3
        accent.GradientColor = 0x01FFFFFF
        data = DATA()
        data.Attribute = 19
        data.Data = ctypes.pointer(accent)
        data.SizeOfData = ctypes.sizeof(accent)
        ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
    except Exception:
        pass

# =========================================================
# NAVIGATION DOT
# =========================================================
class NavDotButton(QPushButton):
    navigateRequested = pyqtSignal(int)
    def __init__(self, color, index, parent=None):
        super().__init__(parent)
        self.page_index = index
        self.setFixedSize(12, 12)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"QPushButton {{ background: {color}; border-radius: 6px; border: none; }} QPushButton:hover {{ background: {color}; border: 1px solid white; }}")
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.navigateRequested.emit(self.page_index)
        super().mousePressEvent(e)
    def mouseDoubleClickEvent(self, e):
        e.accept()

# =========================================================
# TOAST NOTIFICATION
# =========================================================
class ToastNotification(QWidget):
    def __init__(self, message, success=True, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self._opacity = 0.0
        self._success = success

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        icon = QLabel("✅" if success else "🔴")
        icon.setStyleSheet("font-size: 14px; background: transparent; border: none;")
        layout.addWidget(icon)

        lbl = QLabel(message)
        lbl.setStyleSheet("color: white; font-size: 12px; font-weight: 600; background: transparent; border: none;")
        layout.addWidget(lbl)

        self.adjustSize()
        self.setFixedHeight(44)
        self.setMinimumWidth(220)

        # Fade in
        self._fade_in = QTimer(self)
        self._fade_in.timeout.connect(self._do_fade_in)
        self._fade_in.start(16)

        # Auto dismiss after 2.5s
        QTimer.singleShot(2500, self._start_fade_out)

    def _do_fade_in(self):
        self._opacity = min(1.0, self._opacity + 0.08)
        self.setWindowOpacity(self._opacity)
        if self._opacity >= 1.0:
            self._fade_in.stop()

    def _start_fade_out(self):
        self._fade_out = QTimer(self)
        self._fade_out.timeout.connect(self._do_fade_out)
        self._fade_out.start(16)

    def _do_fade_out(self):
        self._opacity = max(0.0, self._opacity - 0.06)
        self.setWindowOpacity(self._opacity)
        if self._opacity <= 0.0:
            self._fade_out.stop()
            self.close()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(30, 42, 30, 230) if self._success else QColor(42, 20, 20, 230)
        p.setBrush(QBrush(color))
        border_color = QColor("#27c93f") if self._success else QColor("#ff5f56")
        p.setPen(QPen(border_color, 1))
        p.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)


def show_toast(message, success=True):
    screen = QApplication.primaryScreen().availableGeometry()
    toast = ToastNotification(message, success)
    toast.adjustSize()
    x = screen.right() - toast.width() - 20
    y = screen.bottom() - toast.height() - 20
    toast.move(x, y)
    toast.setWindowOpacity(0.0)
    toast.show()
    # Keep reference so Python doesn't garbage collect it
    if not hasattr(show_toast, '_active'):
        show_toast._active = []
    show_toast._active.append(toast)
    toast.destroyed.connect(lambda: show_toast._active.remove(toast) if toast in show_toast._active else None)


# =========================================================
# FLOATING BUBBLE (minimized state)
# =========================================================
class FloatingBubble(QWidget):
    restore_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(60, 60)
        self._drag_pos = None

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Outer glow
        p.setBrush(QBrush(QColor(0, 212, 255, 40)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(2, 2, 56, 56)
        # Main circle
        p.setBrush(QBrush(QColor(18, 22, 30, 230)))
        p.setPen(QPen(QColor(0, 212, 255), 2))
        p.drawEllipse(6, 6, 48, 48)
        # Letter
        p.setPen(QColor(0, 212, 255))
        p.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "A")

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.restore_requested.emit()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None


# =========================================================
# MAIN WINDOW
# =========================================================
class AlvensAIWindow(QWidget):
    WINDOW_W = 400
    WINDOW_H = 550

    def __init__(self):
        super().__init__()
        self.drag_pos = None
        self.current_loading_name = ""
        self.loading_value = 0
        self._loading_direction = 1
        self.dashboard_toggles = {}
        self.pref_toggles = {}

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(self.WINDOW_W, self.WINDOW_H)

        self._blur_timer = QTimer(self)
        self._blur_timer.setSingleShot(True)
        self._blur_timer.timeout.connect(self.apply_blur)
        self._blur_timer.start(50)

        self.loading_timer = QTimer(self)
        self.loading_timer.timeout.connect(self.run_loading_animation)

        self.setup_system_tray()

        # AI background agent
        self.agent = AIAgent(self)
        self.agent.ram_alert.connect(self._on_ram_alert)
        self.agent.start()

        # Floating bubble for minimized state
        self.bubble = FloatingBubble()
        self.bubble.restore_requested.connect(self.restore_from_bubble)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.shell = QFrame()
        self.shell.setObjectName("shell")
        self.shell.setStyleSheet("QFrame#shell { background: rgba(18, 22, 30, 220); border-radius: 20px; border: none; }")
        shell_lay = QVBoxLayout(self.shell)
        shell_lay.setContentsMargins(16, 12, 16, 16)
        shell_lay.setSpacing(12)

        # Top Bar
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)

        self.dot_dashboard = NavDotButton("#ff5f56", 0)
        self.dot_preferences = NavDotButton("#ffbd2e", 1)
        self.dot_about = NavDotButton("#27c93f", 2)
        self.dot_aimode = NavDotButton("#a78bfa", 3)

        self.dot_dashboard.navigateRequested.connect(self.switch_page)
        self.dot_preferences.navigateRequested.connect(self.switch_page)
        self.dot_about.navigateRequested.connect(self.switch_page)
        self.dot_aimode.navigateRequested.connect(self.switch_page)

        top.addWidget(self.dot_dashboard)
        top.addWidget(self.dot_preferences)
        top.addWidget(self.dot_about)
        top.addWidget(self.dot_aimode)
        top.addStretch()

        self.title = QLabel("ALVENS AI")
        self.title.setStyleSheet("color: #00d4ff; font-weight: 800; font-size: 15px; letter-spacing: 1.5px; border: none; background: transparent;")
        top.addWidget(self.title)
        top.addStretch()

        self.btn_min = QPushButton("–")
        self.btn_min.setFixedSize(18, 18)
        self.btn_min.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_min.setStyleSheet("QPushButton { color: white; border: none; background: transparent; font-size: 16px; } QPushButton:hover { color: #00d4ff; }")
        self.btn_min.clicked.connect(self.minimize_to_bubble)

        self.btn_close = QPushButton("×")
        self.btn_close.setFixedSize(18, 18)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet("QPushButton { color: white; border: none; background: transparent; font-size: 18px; } QPushButton:hover { color: #ff5f56; }")
        self.btn_close.clicked.connect(self.close)

        top.addWidget(self.btn_min)
        top.addWidget(self.btn_close)
        shell_lay.addLayout(top)

        # Stack
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent; border: none;")

        self.page_dashboard = build_dashboard_page(self)
        self.page_preferences = build_preferences_page(self)
        self.page_about = build_about_page()
        self.page_aimode = build_ai_mode_page(self, self.agent)

        self.stack.addWidget(self.page_dashboard)
        self.stack.addWidget(self.page_preferences)
        self.stack.addWidget(self.page_about)
        self.stack.addWidget(self.page_aimode)

        shell_lay.addWidget(self.stack, 1)

        # Status
        self.status = QLabel("● Ready")
        self.status.setFixedHeight(32)
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet("QLabel { color: #00d4ff; font-size: 11px; font-weight: 600; border: none; background: rgba(0, 212, 255, 0.06); border-radius: 8px; }")
        shell_lay.addWidget(self.status)

        root.addWidget(self.shell)

    # ========== SYSTEM TRAY ==========
    def setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        tray_icon_pixmap = QPixmap(64, 64)
        tray_icon_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(tray_icon_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(0, 212, 255)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(8, 8, 48, 48)
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        painter.drawText(tray_icon_pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "A")
        painter.end()
        self.tray_icon.setIcon(QIcon(tray_icon_pixmap))
        
        tray_menu = QMenu()
        restore_action = QAction("Restore Window", self)
        restore_action.triggered.connect(self.restore_from_tray)
        tray_menu.addAction(restore_action)
        tray_menu.addSeparator()
        dashboard_action = QAction("📊 Dashboard", self)
        dashboard_action.triggered.connect(lambda: self.switch_page_from_tray(0))
        tray_menu.addAction(dashboard_action)
        prefs_action = QAction("⚙️ Preferences", self)
        prefs_action.triggered.connect(lambda: self.switch_page_from_tray(1))
        tray_menu.addAction(prefs_action)
        about_action = QAction("ℹ️ About AI", self)
        about_action.triggered.connect(lambda: self.switch_page_from_tray(2))
        tray_menu.addAction(about_action)
        tray_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()
        
    def minimize_to_bubble(self):
        if getattr(self, 'float_icon_enabled', True):
            # Float icon ON → show draggable bubble
            center = self.geometry().center()
            self.bubble.move(center.x() - 30, center.y() - 30)
            self.hide()
            self.bubble.show()
        else:
            # Float icon OFF → normal OS minimize
            self.showMinimized()

    def restore_from_bubble(self):
        self.bubble.hide()
        self.stack.setCurrentIndex(0)
        self.switch_page(0)
        self.show()
        self.activateWindow()
        self.raise_()

    def restore_from_tray(self):
        self.show()
        self.activateWindow()
        self.raise_()
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.show()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()
        
    def switch_page_from_tray(self, index):
        self.show()
        self.activateWindow()
        self.stack.setCurrentIndex(index)
        if index == 0:
            self.title.setStyleSheet("color: #00d4ff; font-weight: 800; font-size: 15px; border: none; background: transparent;")
            self.status.setText("● Dashboard Ready")
        elif index == 1:
            self.title.setStyleSheet("color: #ffbd2e; font-weight: 800; font-size: 15px; border: none; background: transparent;")
            self.status.setText("⚙️ Settings Ready")
        elif index == 2:
            self.title.setStyleSheet("color: #27c93f; font-weight: 800; font-size: 15px; border: none; background: transparent;")
            self.status.setText("✨ About AI")
        
    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.restore_from_tray()

    def _on_ram_alert(self, name, pid, ram_mb):
        self.tray_icon.showMessage(
            "⚠️ Alvens AI — High RAM",
            f"{name} is using {ram_mb} MB of RAM.\n"
            f"Consider closing it to free up memory.",
            QSystemTrayIcon.MessageIcon.Warning,
            6000
        )

    # ========== HANDLERS ==========
    def handle_dashboard_toggle(self, name, checked):
        self.current_loading_name = name
        self.loading_timer.stop()
        if checked:
            # Always start fresh from 0
            self.loading_value = 0
            self.progress_ring.progress = 0
            self.progress_ring.target = 0
            self.progress_ring.update()
            self._loading_direction = 1   # going up
            self.status.setText(f"⚡ Loading {name}...")
            self.loading_timer.start(20)
        else:
            # Animate back down to 0
            self._loading_direction = -1
            self.status.setText(f"● {name}: OFF")
            self.loading_timer.start(20)

    def run_loading_animation(self):
        if self._loading_direction == 1:
            # Animate 0 → 100
            if self.loading_value < 100:
                self.loading_value += 2
                self.progress_ring.set_progress(self.loading_value)
            else:
                self.loading_timer.stop()
                self.status.setText(f"✅ {self.current_loading_name}: ON")
        else:
            # Animate back → 0
            if self.loading_value > 0:
                self.loading_value -= 2
                self.progress_ring.set_progress(self.loading_value)
            else:
                self.loading_timer.stop()

    def on_ai_level_changed(self, value):
        if value < 34:
            level = "Low"
        elif value < 67:
            level = "Mid"
        else:
            level = "High"
        self.status.setText(f"🎚️ AI Level: {level} ({value}%)")

    def switch_page(self, index):
        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)
            if index == 0:
                self.status.setText("● Dashboard Ready")
                self.title.setStyleSheet("color: #00d4ff; font-weight: 800; font-size: 15px; border: none; background: transparent;")
            elif index == 1:
                self.status.setText("⚙️ Settings Ready")
                self.title.setStyleSheet("color: #ffbd2e; font-weight: 800; font-size: 15px; border: none; background: transparent;")
            elif index == 2:
                self.status.setText("✨ About AI")
                self.title.setStyleSheet("color: #27c93f; font-weight: 800; font-size: 15px; border: none; background: transparent;")
            elif index == 3:
                self.status.setText("🤖 AI Mode Active")
                self.title.setStyleSheet("color: #a78bfa; font-weight: 800; font-size: 15px; border: none; background: transparent;")

    def apply_blur(self):
        try:
            set_blur(int(self.winId()))
        except Exception:
            pass

    def closeEvent(self, event):
        if hasattr(self, 'agent'):
            self.agent.stop()
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
        if hasattr(self, 'bubble'):
            self.bubble.hide()
        event.accept()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = e.globalPosition().toPoint()

    def mouseMoveEvent(self, e):
        if self.drag_pos and e.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + e.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = e.globalPosition().toPoint()

    def mouseReleaseEvent(self, e):
        self.drag_pos = None

# =========================================================
# RUN
# =========================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    win = AlvensAIWindow()
    win.show()
    sys.exit(app.exec())