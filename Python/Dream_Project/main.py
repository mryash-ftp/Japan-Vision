import sys
import os
import ctypes
import platform

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame,
    QLabel, QStackedWidget, QSlider, QSizePolicy, QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QColor, QBrush, QPen, QLinearGradient, QFont, QIcon, QAction, QPixmap
)

# =========================================================
# WINDOWS BLUR
# =========================================================
def set_blur(hwnd):
    try:
        class ACCENT_POLICY(ctypes.Structure):
            _fields_ = [
                ("AccentState", ctypes.c_int),
                ("AccentFlags", ctypes.c_int),
                ("GradientColor", ctypes.c_int),
                ("AnimationId", ctypes.c_int)
            ]

        class DATA(ctypes.Structure):
            _fields_ = [
                ("Attribute", ctypes.c_int),
                ("Data", ctypes.POINTER(ACCENT_POLICY)),
                ("SizeOfData", ctypes.c_size_t)
            ]

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
        self.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{
                background: {color};
                border: 1px solid white;
            }}
        """)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.navigateRequested.emit(self.page_index)
        super().mousePressEvent(e)

    def mouseDoubleClickEvent(self, e):
        e.accept()


# =========================================================
# TOGGLE SWITCH
# =========================================================
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
            self.setStyleSheet("""
                QPushButton {
                    background: #00d4ff;
                    color: white;
                    border: none;
                    border-radius: 14px;
                    font-weight: 700;
                    font-size: 10px;
                }
            """)
        else:
            self.setText(self.off_text)
            self.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.12);
                    color: rgba(255,255,255,0.9);
                    border: none;
                    border-radius: 14px;
                    font-weight: 700;
                    font-size: 10px;
                }
            """)


# =========================================================
# CIRCULAR PROGRESS
# =========================================================
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

        # Outer ring - thin and subtle
        p.setPen(QPen(QColor(255, 255, 255, 20), 6))
        p.drawEllipse(15, 15, 100, 100)

        # Progress arc
        grad = QLinearGradient(0, 0, 130, 130)
        grad.setColorAt(0, QColor("#00d4ff"))
        grad.setColorAt(1, QColor("#27c93f"))
        p.setPen(QPen(QBrush(grad), 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        
        angle = int(360 * self.progress / 100)
        if angle > 0:
            p.drawArc(15, 15, 100, 100, 90 * 16, -angle * 16)

        # Center text
        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{self.progress}%")


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
        self.dashboard_toggles = {}
        self.pref_toggles = {}

        # Window setup
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(self.WINDOW_W, self.WINDOW_H)

        # Apply blur
        self._blur_timer = QTimer(self)
        self._blur_timer.setSingleShot(True)
        self._blur_timer.timeout.connect(self.apply_blur)
        self._blur_timer.start(50)

        # Loading timer
        self.loading_timer = QTimer(self)
        self.loading_timer.timeout.connect(self.run_loading_animation)

        # Setup system tray
        self.setup_system_tray()

        # Root layout - NO EXTRA MARGINS
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Main shell - CLEAN, SINGLE LAYER
        self.shell = QFrame()
        self.shell.setObjectName("shell")
        self.shell.setStyleSheet("""
            QFrame#shell {
                background: rgba(18, 22, 30, 220);
                border-radius: 20px;
                border: none;
            }
        """)
        shell_lay = QVBoxLayout(self.shell)
        shell_lay.setContentsMargins(16, 12, 16, 16)
        shell_lay.setSpacing(12)

        # ---------------- TOP BAR ----------------
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)

        self.dot_dashboard = NavDotButton("#ff5f56", 0)
        self.dot_preferences = NavDotButton("#ffbd2e", 1)
        self.dot_about = NavDotButton("#27c93f", 2)

        self.dot_dashboard.navigateRequested.connect(self.switch_page)
        self.dot_preferences.navigateRequested.connect(self.switch_page)
        self.dot_about.navigateRequested.connect(self.switch_page)

        top.addWidget(self.dot_dashboard)
        top.addWidget(self.dot_preferences)
        top.addWidget(self.dot_about)
        top.addStretch()

        self.title = QLabel("ALVENS AI")
        self.title.setStyleSheet("""
            color: #00d4ff;
            font-weight: 800;
            font-size: 15px;
            letter-spacing: 1.5px;
            border: none;
            background: transparent;
        """)
        top.addWidget(self.title)
        top.addStretch()

        self.btn_min = QPushButton("–")
        self.btn_min.setFixedSize(18, 18)
        self.btn_min.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_min.setStyleSheet("""
            QPushButton {
                color: white;
                border: none;
                background: transparent;
                font-size: 16px;
            }
            QPushButton:hover { color: #00d4ff; }
        """)
        self.btn_min.clicked.connect(self.minimize_to_tray)

        self.btn_close = QPushButton("×")
        self.btn_close.setFixedSize(18, 18)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                color: white;
                border: none;
                background: transparent;
                font-size: 18px;
            }
            QPushButton:hover { color: #ff5f56; }
        """)
        self.btn_close.clicked.connect(self.close)

        top.addWidget(self.btn_min)
        top.addWidget(self.btn_close)

        shell_lay.addLayout(top)

        # ---------------- STACK ----------------
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent; border: none;")

        self.page_dashboard = self.build_dashboard_page()
        self.page_preferences = self.build_preferences_page()
        self.page_about = self.build_about_page()

        self.stack.addWidget(self.page_dashboard)
        self.stack.addWidget(self.page_preferences)
        self.stack.addWidget(self.page_about)

        shell_lay.addWidget(self.stack, 1)

        # ---------------- STATUS ----------------
        self.status = QLabel("● Ready")
        self.status.setFixedHeight(32)
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet("""
            QLabel {
                color: #00d4ff;
                font-size: 11px;
                font-weight: 600;
                border: none;
                background: rgba(0, 212, 255, 0.06);
                border-radius: 8px;
            }
        """)
        shell_lay.addWidget(self.status)

        root.addWidget(self.shell)

    # =====================================================
    # SYSTEM TRAY SETUP
    # =====================================================
    def setup_system_tray(self):
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Create a simple icon (colored circle)
        tray_icon_pixmap = QPixmap(64, 64)
        tray_icon_pixmap.fill(Qt.GlobalColor.transparent)
        
        # Draw a nice icon
        painter = QPainter(tray_icon_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(0, 212, 255)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(8, 8, 48, 48)
        
        # Draw "A" letter
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        painter.drawText(tray_icon_pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "A")
        painter.end()
        
        self.tray_icon.setIcon(QIcon(tray_icon_pixmap))
        
        # Create context menu
        tray_menu = QMenu()
        
        # Restore action
        restore_action = QAction("Restore Window", self)
        restore_action.triggered.connect(self.restore_from_tray)
        tray_menu.addAction(restore_action)
        
        tray_menu.addSeparator()
        
        # Dashboard action
        dashboard_action = QAction("📊 Dashboard", self)
        dashboard_action.triggered.connect(lambda: self.switch_page_from_tray(0))
        tray_menu.addAction(dashboard_action)
        
        # Preferences action
        prefs_action = QAction("⚙️ Preferences", self)
        prefs_action.triggered.connect(lambda: self.switch_page_from_tray(1))
        tray_menu.addAction(prefs_action)
        
        # About action
        about_action = QAction("ℹ️ About AI", self)
        about_action.triggered.connect(lambda: self.switch_page_from_tray(2))
        tray_menu.addAction(about_action)
        
        tray_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        
        # Double-click on tray icon to restore
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        
        # Show tray icon
        self.tray_icon.show()
        
    def minimize_to_tray(self):
        """Minimize window to system tray"""
        self.hide()
        self.tray_icon.showMessage(
            "Alvens AI",
            "Application minimized to system tray.\nDouble-click to restore.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
        
    def restore_from_tray(self):
        """Restore window from system tray"""
        self.show()
        self.activateWindow()
        self.raise_()
        # Ensure window is on top
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.show()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()
        
    def switch_page_from_tray(self, index):
        """Switch page when triggered from tray"""
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
        """Handle tray icon activation (double-click)"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.restore_from_tray()

    # =====================================================
    # DASHBOARD PAGE
    # =====================================================
    def build_dashboard_page(self):
        page = QWidget()
        page.setStyleSheet("background: transparent; border: none;")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 10, 0, 0)
        lay.setSpacing(16)

        heading = QLabel("⚡ DASHBOARD")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heading.setStyleSheet("""
            color: #00d4ff;
            font-size: 17px;
            font-weight: 800;
            letter-spacing: 1px;
            border: none;
            background: transparent;
        """)
        lay.addWidget(heading)

        self.progress_ring = CircularProgress()
        lay.addWidget(self.progress_ring, alignment=Qt.AlignmentFlag.AlignCenter)

        toggles = [("🚀", "AI TURBO"), ("👻", "GHOST MODE"), ("🛡️", "SAFE MODE")]
        for icon, name in toggles:
            card = self.create_toggle_card(icon, name)
            lay.addWidget(card)

        lay.addStretch()
        return page

    # =====================================================
    # PREFERENCES PAGE - FULL CONTENT
    # =====================================================
    def build_preferences_page(self):
        page = QWidget()
        page.setStyleSheet("background: transparent; border: none;")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 10, 0, 0)
        lay.setSpacing(14)

        heading = QLabel("⚙️ PREFERENCES")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heading.setStyleSheet("""
            color: #ffbd2e;
            font-size: 17px;
            font-weight: 800;
            letter-spacing: 1px;
            border: none;
            background: transparent;
        """)
        lay.addWidget(heading)

        # Welcome Card
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

        # System Preferences Section
        section = QLabel("⚡ SYSTEM PREFERENCES")
        section.setStyleSheet("""
            color: #ffbd2e;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.5px;
            margin-top: 4px;
            background: transparent;
        """)
        lay.addWidget(section)

        # Preference toggles
        prefs = [("🔄", "AUTO START", False), ("🌙", "DARK MODE", True), ("🔔", "NOTIFICATIONS", True)]
        for icon, name, initial in prefs:
            card = self.create_pref_card(icon, name, initial)
            lay.addWidget(card)

        # Performance Section
        perf_label = QLabel("🔊 PERFORMANCE LEVEL")
        perf_label.setStyleSheet("""
            color: #ffbd2e;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.5px;
            margin-top: 4px;
            background: transparent;
        """)
        lay.addWidget(perf_label)

        # Slider Card
        slider_card = QFrame()
        slider_card.setStyleSheet("background: rgba(255,255,255,0.04); border-radius: 12px; border: none;")
        slider_lay = QVBoxLayout(slider_card)
        slider_lay.setContentsMargins(16, 12, 16, 10)
        slider_lay.setSpacing(6)

        self.ai_slider = QSlider(Qt.Orientation.Horizontal)
        self.ai_slider.setRange(0, 100)
        self.ai_slider.setValue(65)
        self.ai_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ai_slider.valueChanged.connect(self.on_ai_level_changed)
        self.ai_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 3px;
                background: rgba(255,255,255,0.15);
                border-radius: 1.5px;
            }
            QSlider::sub-page:horizontal {
                background: #ffbd2e;
                border-radius: 1.5px;
            }
            QSlider::handle:horizontal {
                background: #ffbd2e;
                width: 12px;
                height: 12px;
                margin: -4.5px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background: #ffd15a;
            }
        """)
        slider_lay.addWidget(self.ai_slider)

        levels = QHBoxLayout()
        for level in ["Low", "Mid", "High"]:
            lbl = QLabel(level)
            lbl.setStyleSheet("color: rgba(255,255,255,0.55); font-size: 10px; background: transparent;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            levels.addWidget(lbl)
        slider_lay.addLayout(levels)

        lay.addWidget(slider_card)
        lay.addStretch()
        return page

    # =====================================================
    # ABOUT PAGE - PROPER SPACING & HORIZONTAL LINES
    # =====================================================
    def build_about_page(self):
        page = QWidget()
        page.setStyleSheet("background: transparent; border: none;")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 10, 0, 0)
        lay.setSpacing(0)

        heading = QLabel("✨ ABOUT AI ✨")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heading.setStyleSheet("""
            color: #27c93f;
            font-size: 18px;
            font-weight: 800;
            letter-spacing: 2px;
            border: none;
            margin-bottom: 20px;
            background: transparent;
        """)
        lay.addWidget(heading)

        # Main Container - NO BORDER
        container = QFrame()
        container.setStyleSheet("background: transparent; border: none;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 0, 10, 0)
        container_layout.setSpacing(0)

        # Item 1 - Founder
        founder_title = QLabel("FOUNDER")
        founder_title.setStyleSheet("""
            color: #27c93f;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1.5px;
            border: none;
            margin-bottom: 6px;
            background: transparent;
        """)
        container_layout.addWidget(founder_title)
        
        founder_name = QLabel("Alven Alex [ Pradeep Kumar Gupta]")
        founder_name.setStyleSheet("""
            color: white;
            font-size: 15px;
            font-weight: 600;
            border: none;
            margin-bottom: 15px;
            background: transparent;
        """)
        container_layout.addWidget(founder_name)


        # Item 2 - Language
        lang_title = QLabel("LANGUAGE")
        lang_title.setStyleSheet("""
            color: #27c93f;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1.5px;
            border: none;
            margin-bottom: 6px;
            background: transparent;
        """)
        container_layout.addWidget(lang_title)
        
        lang_name = QLabel("Python")
        lang_name.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: 500;
            border: none;
            margin-bottom: 15px;
            background: transparent;
        """)
        container_layout.addWidget(lang_name)


        # Item 3 - UI Style
        ui_title = QLabel("UI STYLE")
        ui_title.setStyleSheet("""
            color: #27c93f;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1.5px;
            border: none;
            margin-bottom: 6px;
            background: transparent;
        """)
        container_layout.addWidget(ui_title)
        
        ui_name = QLabel("Glassmorphism / Modern")
        ui_name.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: 500;
            border: none;
            margin-bottom: 15px;
            background: transparent;
        """)
        container_layout.addWidget(ui_name)


        # Item 4 - Features
        features_title = QLabel("FEATURES")
        features_title.setStyleSheet("""
            color: #27c93f;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1.5px;
            border: none;
            margin-bottom: 6px;
            background: transparent;
        """)
        container_layout.addWidget(features_title)
        
        features_list = QLabel("• Turbo Mode\n• Ghost Mode\n• Safe Mode")
        features_list.setStyleSheet("""
            color: rgba(255,255,255,0.9);
            font-size: 13px;
            font-weight: 500;
            border: none;
            line-height: 1.6;
            margin-bottom: 15px;
            background: transparent;
        """)
        container_layout.addWidget(features_list)


        # Item 5 - Version
        version_title = QLabel("VERSION")
        version_title.setStyleSheet("""
            color: #27c93f;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1.5px;
            border: none;
            margin-bottom: 6px;
            background: transparent;
        """)
        container_layout.addWidget(version_title)
        
        version_num = QLabel("2.0.0")
        version_num.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: 600;
            border: none;
            margin-bottom: 20px;
            background: transparent;
        """)
        container_layout.addWidget(version_num)

        lay.addWidget(container)
        lay.addStretch()

        # Quote at bottom
        quote = QLabel("“Unlock More Features With Alvens OS”")
        quote.setAlignment(Qt.AlignmentFlag.AlignCenter)
        quote.setStyleSheet("""
            color: rgba(39, 201, 63, 0.6);
            font-size: 9px;
            font-style: italic;
            border: none;
            margin-top: 10px;
            background: transparent;
        """)
        lay.addWidget(quote)

        return page

    # =====================================================
    # HELPERS
    # =====================================================
    def create_toggle_card(self, icon, name):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.04);
                border-radius: 12px;
                border: none;
            }
        """)
        lay = QHBoxLayout(card)
        lay.setContentsMargins(14, 10, 14, 10)

        lbl = QLabel(f"{icon} {name}")
        lbl.setStyleSheet("""
            color: white;
            font-size: 13px;
            font-weight: 600;
            border: none;
            background: transparent;
        """)

        toggle = ToggleSwitch(False)
        toggle.toggledAnimated.connect(lambda checked, n=name: self.handle_dashboard_toggle(n, checked))

        lay.addWidget(lbl)
        lay.addStretch()
        lay.addWidget(toggle)
        
        # Store toggle reference
        self.dashboard_toggles[name] = toggle
        return card

    def create_pref_card(self, icon, name, initial):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.04);
                border-radius: 12px;
                border: none;
            }
        """)
        lay = QHBoxLayout(card)
        lay.setContentsMargins(14, 10, 14, 10)

        lbl = QLabel(f"{icon} {name}")
        lbl.setStyleSheet("""
            color: white;
            font-size: 13px;
            font-weight: 600;
            border: none;
            background: transparent;
        """)

        toggle = ToggleSwitch(initial)
        lay.addWidget(lbl)
        lay.addStretch()
        lay.addWidget(toggle)
        
        # Store toggle reference
        self.pref_toggles[name] = toggle
        return card

    # =====================================================
    # HANDLERS
    # =====================================================
    def handle_dashboard_toggle(self, name, checked):
        self.current_loading_name = name
        if checked:
            self.loading_value = 0
            self.progress_ring.set_progress(0)
            self.status.setText(f"⚡ Loading {name}...")
            self.loading_timer.start(20)
        else:
            self.loading_timer.stop()
            self.progress_ring.set_progress(0)
            self.status.setText(f"● {name}: OFF")

    def run_loading_animation(self):
        if self.loading_value < 100:
            self.loading_value += 2
            self.progress_ring.set_progress(self.loading_value)
        else:
            self.loading_timer.stop()
            self.status.setText(f"✅ {self.current_loading_name}: ON")

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

    def apply_blur(self):
        try:
            set_blur(int(self.winId()))
        except Exception:
            pass

    def closeEvent(self, event):
        """Handle close event - remove tray icon"""
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
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
    
    # Set application icon for tray
    app.setQuitOnLastWindowClosed(False)
    
    win = AlvensAIWindow()
    win.show()
    sys.exit(app.exec())
