"""
AI Mode Page — UI for the background AI Agent
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal


class ToggleSwitch(QPushButton):
    toggledAnimated = pyqtSignal(bool)
    def __init__(self, initial=False, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(initial)
        self.setFixedSize(58, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self._emit)
        self._refresh()
    def _emit(self):
        self._refresh()
        self.toggledAnimated.emit(self.isChecked())
    def _refresh(self):
        if self.isChecked():
            self.setText("ON")
            self.setStyleSheet("QPushButton{background:#00d4ff;color:white;border:none;border-radius:14px;font-weight:700;font-size:10px;}")
        else:
            self.setText("OFF")
            self.setStyleSheet("QPushButton{background:rgba(255,255,255,0.12);color:rgba(255,255,255,0.9);border:none;border-radius:14px;font-weight:700;font-size:10px;}")


def _card(parent_layout, label_text, toggle_initial, on_toggle):
    card = QFrame()
    card.setStyleSheet("QFrame{background:rgba(255,255,255,0.04);border-radius:12px;border:none;}")
    lay = QHBoxLayout(card)
    lay.setContentsMargins(14, 10, 14, 10)
    lbl = QLabel(label_text)
    lbl.setStyleSheet("color:white;font-size:12px;font-weight:600;border:none;background:transparent;")
    t = ToggleSwitch(toggle_initial)
    t.toggledAnimated.connect(on_toggle)
    lay.addWidget(lbl)
    lay.addStretch()
    lay.addWidget(t)
    parent_layout.addWidget(card)
    return t


def _stat_row(label, value_text):
    row = QFrame()
    row.setStyleSheet("QFrame{background:rgba(255,255,255,0.03);border-radius:8px;border:none;}")
    lay = QHBoxLayout(row)
    lay.setContentsMargins(12, 6, 12, 6)
    lbl = QLabel(label)
    lbl.setStyleSheet("color:rgba(255,255,255,0.6);font-size:11px;border:none;background:transparent;")
    val = QLabel(value_text)
    val.setStyleSheet("color:#00d4ff;font-size:11px;font-weight:700;border:none;background:transparent;")
    val.setAlignment(Qt.AlignmentFlag.AlignRight)
    lay.addWidget(lbl)
    lay.addStretch()
    lay.addWidget(val)
    return row, val


def build_ai_mode_page(parent, agent):
    page = QWidget()
    page.setStyleSheet("background:transparent;border:none;")
    outer = QVBoxLayout(page)
    outer.setContentsMargins(0, 10, 0, 0)
    outer.setSpacing(10)

    # heading
    heading = QLabel("🤖 AI MODE")
    heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
    heading.setStyleSheet("color:#a78bfa;font-size:17px;font-weight:800;letter-spacing:1px;border:none;background:transparent;")
    outer.addWidget(heading)

    # status badge
    parent.ai_status_lbl = QLabel("⚪ Initializing...")
    parent.ai_status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    parent.ai_status_lbl.setStyleSheet(
        "color:#a78bfa;font-size:11px;font-weight:600;background:rgba(167,139,250,0.08);"
        "border-radius:8px;padding:4px 0;border:none;"
    )
    outer.addWidget(parent.ai_status_lbl)

    # scroll area
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setStyleSheet(
        "QScrollArea{border:none;background:transparent;}"
        "QScrollBar:vertical{width:4px;background:transparent;}"
        "QScrollBar::handle:vertical{background:rgba(167,139,250,0.3);border-radius:2px;}"
    )
    inner = QWidget()
    inner.setStyleSheet("background:transparent;")
    lay = QVBoxLayout(inner)
    lay.setContentsMargins(0, 0, 4, 0)
    lay.setSpacing(8)
    scroll.setWidget(inner)
    outer.addWidget(scroll, 1)

    # controls
    sec1 = QLabel("⚙️ CONTROLS")
    sec1.setStyleSheet("color:#a78bfa;font-size:11px;font-weight:700;background:transparent;")
    lay.addWidget(sec1)

    _card(lay, "🤖  AI Agent Active", agent.enabled,
          lambda v: _toggle_agent(v, agent, parent))

    # live stats
    sec2 = QLabel("📊 LIVE SYSTEM STATS")
    sec2.setStyleSheet("color:#a78bfa;font-size:11px;font-weight:700;background:transparent;margin-top:4px;")
    lay.addWidget(sec2)

    stats_card = QFrame()
    stats_card.setStyleSheet("QFrame{background:rgba(255,255,255,0.04);border-radius:12px;border:none;}")
    stats_lay = QVBoxLayout(stats_card)
    stats_lay.setContentsMargins(0, 6, 0, 6)
    stats_lay.setSpacing(2)

    r_cpu,  parent.ai_cpu_val  = _stat_row("  CPU",     "—")
    r_ram,  parent.ai_ram_val  = _stat_row("  RAM",     "—")
    r_disk, parent.ai_disk_val = _stat_row("  Disk",    "—")
    r_net,  parent.ai_net_val  = _stat_row("  Network", "—")

    for r in (r_cpu, r_ram, r_disk, r_net):
        stats_lay.addWidget(r)
    lay.addWidget(stats_card)

    # last alert box
    sec3 = QLabel("⚠️ LAST RAM ALERT")
    sec3.setStyleSheet("color:#a78bfa;font-size:11px;font-weight:700;background:transparent;margin-top:4px;")
    lay.addWidget(sec3)

    parent.ai_alert_box = QLabel("No alerts yet — RAM is healthy ✅")
    parent.ai_alert_box.setWordWrap(True)
    parent.ai_alert_box.setStyleSheet(
        "color:#fbbf24;font-size:11px;background:rgba(251,191,36,0.07);"
        "border-radius:10px;padding:8px 12px;border:none;"
    )
    lay.addWidget(parent.ai_alert_box)
    lay.addStretch()

    # wire signals
    agent.stats_updated.connect(lambda c, r, d, n: _update_stats(parent, c, r, d, n))
    agent.status_changed.connect(lambda s: parent.ai_status_lbl.setText(s))
    agent.ram_alert.connect(lambda name, pid, mb: parent.ai_alert_box.setText(
        f"⚠️ {name} (pid {pid}) is using {mb} MB\nConsider closing it to free RAM."
    ))

    return page


def _toggle_agent(enabled, agent, parent):
    agent.enabled = enabled
    if enabled:
        agent.start()
    else:
        agent.stop()


def _update_stats(parent, cpu, ram, disk, net):
    parent.ai_cpu_val.setText(f"{cpu:.1f}%")
    parent.ai_ram_val.setText(f"{ram:.1f}%")
    parent.ai_disk_val.setText(f"{disk:.1f}%")
    parent.ai_net_val.setText(f"{net:.2f} MB/s")
