"""
Alvens AI - Background System Agent
=====================================
- Monitors total system RAM usage
- When RAM >= 90%, finds the top RAM-eating non-essential process
- Shows a Windows toast notification suggesting to close it
- NO auto-suspend, NO auto-kill — user is always in control
- Local only, no cloud, no telemetry
"""

import threading
import time
import psutil
from PyQt6.QtCore import QObject, pyqtSignal

# ── How often to check (seconds) ──────────────────────────
MONITOR_INTERVAL  = 5      # scan every 5s
RAM_ALERT_PERCENT = 90.0   # only alert when total RAM >= 90%
ALERT_COOLDOWN    = 60     # don't re-alert same process within 60s

# ── Processes we never suggest closing ────────────────────
WHITELIST = {
    "system", "smss.exe", "csrss.exe", "wininit.exe", "winlogon.exe",
    "services.exe", "lsass.exe", "svchost.exe", "explorer.exe",
    "dwm.exe", "taskmgr.exe", "python.exe", "pythonw.exe",
    "registry", "memory compression",
}


class AIAgent(QObject):
    # ── signals ───────────────────────────────────────────
    stats_updated  = pyqtSignal(float, float, float, float)  # cpu, ram, disk, net MB/s
    ram_alert      = pyqtSignal(str, int, float)             # proc name, pid, ram_mb
    status_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.enabled        = True
        self._running       = False
        self._alerted: dict[int, float] = {}   # pid → last alert timestamp
        self._net_last  = psutil.net_io_counters()
        self._net_time  = time.time()

    # ── public ────────────────────────────────────────────
    def start(self):
        if self._running:
            return
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()
        self.status_changed.emit("🟢 AI Agent running")

    def stop(self):
        self._running = False
        self.status_changed.emit("⚪ AI Agent stopped")

    # ── main loop ─────────────────────────────────────────
    def _loop(self):
        while self._running:
            try:
                self._emit_stats()
                if self.enabled:
                    self._check_ram()
            except Exception:
                pass
            time.sleep(MONITOR_INTERVAL)

    def _check_ram(self):
        ram_pct = psutil.virtual_memory().percent
        if ram_pct < RAM_ALERT_PERCENT:
            return  # all good, nothing to do

        # find the biggest RAM user that isn't whitelisted
        top_proc = None
        top_mb   = 0.0

        for proc in psutil.process_iter(["pid", "name"]):
            try:
                name = (proc.info["name"] or "").lower()
                if name in WHITELIST:
                    continue
                mb = proc.memory_info().rss / (1024 * 1024)
                if mb > top_mb:
                    top_mb   = mb
                    top_proc = proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if top_proc is None:
            return

        pid  = top_proc.pid
        name = top_proc.info["name"] or "Unknown"
        now  = time.time()

        # cooldown — don't spam the same process
        if now - self._alerted.get(pid, 0) < ALERT_COOLDOWN:
            return

        self._alerted[pid] = now
        self.ram_alert.emit(name, pid, round(top_mb, 1))
        self.status_changed.emit(f"⚠️ High RAM: {name} using {top_mb:.0f} MB")

    def _emit_stats(self):
        cpu  = psutil.cpu_percent(interval=None)
        ram  = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent

        now     = time.time()
        net_now = psutil.net_io_counters()
        elapsed = max(now - self._net_time, 0.001)
        net_mb  = (
            (net_now.bytes_sent + net_now.bytes_recv) -
            (self._net_last.bytes_sent + self._net_last.bytes_recv)
        ) / (1024 * 1024 * elapsed)
        self._net_last = net_now
        self._net_time = now

        self.stats_updated.emit(cpu, ram, disk, round(net_mb, 2))
