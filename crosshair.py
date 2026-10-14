#!/usr/bin/env python3
"""
Crosshair Overlay
-----------------
A click-through, always-on-top crosshair for borderless-windowed games.

Install:   pip install PyQt5
Optional:  pip install pynput     (enables the global hotkey Ctrl+Alt+C)
Run:       python crosshair.py

Control it from the system tray icon (Show/Hide, Settings, Quit).
Settings are saved to ~/.crosshair_overlay.json
"""

import sys
import json
import ctypes
from pathlib import Path

from PyQt5.QtCore import Qt, QTimer, QRect, QObject, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QDialog, QFormLayout, QComboBox, QSpinBox,
    QCheckBox, QPushButton, QSlider, QHBoxLayout, QVBoxLayout, QLabel,
    QSystemTrayIcon, QMenu, QAction, QColorDialog,
)

CONFIG_PATH = Path.home() / ".crosshair_overlay.json"
STYLES = ["Cross", "T-Shape", "Dot", "Circle"]

DEFAULTS = {
    "style": "Cross",
    "color": "#00ff00",
    "size": 12,            # arm length / circle radius (px)
    "thickness": 2,        # line thickness (px)
    "gap": 4,              # gap between center and arms (px)
    "center_dot": False,
    "dot_size": 2,
    "outline": True,
    "outline_color": "#000000",
    "outline_thickness": 1,
    "opacity": 100,        # percent
    "screen": 0,
    "offset_x": 0,
    "offset_y": 0,
    "visible": True,
}


# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------
def load_config():
    cfg = dict(DEFAULTS)
    try:
        cfg.update(json.loads(CONFIG_PATH.read_text()))
    except Exception:
        pass
    return cfg


def save_config(cfg):
    try:
        CONFIG_PATH.write_text(json.dumps(cfg, indent=2))
    except Exception as e:
        print(f"Could not save config: {e}")


# --------------------------------------------------------------------------
# Overlay window
# --------------------------------------------------------------------------
class Overlay(QWidget):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg

        flags = (
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowTransparentForInput
            | Qt.WindowDoesNotAcceptFocus
        )
        if sys.platform.startswith("linux"):
            flags |= Qt.X11BypassWindowManagerHint
        self.setWindowFlags(flags)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        if sys.platform == "darwin":
            self.setAttribute(Qt.WA_MacAlwaysShowToolWindow)

        self.apply()
        self._click_through_win32()

        # Keep the overlay above borderless-fullscreen games
        self._raise_timer = QTimer(self)
        self._raise_timer.timeout.connect(self._keep_on_top)
        self._raise_timer.start(1500)

    # -- helpers ----------------------------------------------------------
    def _keep_on_top(self):
        if self.cfg["visible"]:
            self.raise_()

    def _click_through_win32(self):
        """Belt-and-braces click-through on Windows."""
        if sys.platform != "win32":
            return
        try:
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020
            WS_EX_TOOLWINDOW = 0x00000080
            WS_EX_NOACTIVATE = 0x08000000
            user32 = ctypes.windll.user32
            hwnd = int(self.winId())
            style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style |= (WS_EX_LAYERED | WS_EX_TRANSPARENT
                      | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE)
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        except Exception as e:
            print(f"Win32 click-through failed: {e}")

    def _canvas_side(self):
        c = self.cfg
        reach = c["gap"] + c["size"] + c["thickness"] + c["outline_thickness"]
        reach = max(reach, c["dot_size"] + c["outline_thickness"])
        side = 2 * (reach + 6)
        return max(side, 32)

    # -- public -----------------------------------------------------------
    def apply(self):
        """Re-size, re-position and repaint from the current config."""
        side = self._canvas_side()
        self.resize(side, side)

        screens = QApplication.screens()
        idx = min(max(self.cfg["screen"], 0), len(screens) - 1)
        g = screens[idx].geometry()
        x = g.x() + g.width() // 2 - side // 2 + self.cfg["offset_x"]
        y = g.y() + g.height() // 2 - side // 2 + self.cfg["offset_y"]
        self.move(x, y)

        if self.cfg["visible"]:
            if not self.isVisible():
                self.show()
                self._click_through_win32()
            self.raise_()
        else:
            self.hide()
        self.update()

    def toggle(self):
        self.cfg["visible"] = not self.cfg["visible"]
        self.apply()
        save_config(self.cfg)

    # -- painting ---------------------------------------------------------
    def paintEvent(self, _event):
        c = self.cfg
        p = QPainter(self)
        p.setOpacity(c["opacity"] / 100.0)

        cx, cy = self.width() // 2, self.height() // 2
        t, g, s = c["thickness"], c["gap"], c["size"]
        o = c["outline_thickness"] if c["outline"] else 0
        color = QColor(c["color"])
        ocolor = QColor(c["outline_color"])

        style = c["style"]
        rects = []
        if style in ("Cross", "T-Shape"):
            half = t // 2
            rects.append(QRect(cx - g - s, cy - half, s, t))   # left
            rects.append(QRect(cx + g, cy - half, s, t))       # right
            rects.append(QRect(cx - half, cy + g, t, s))       # bottom
            if style == "Cross":
                rects.append(QRect(cx - half, cy - g - s, t, s))  # top
        if c["center_dot"] or style == "Dot":
            d = c["dot_size"] if style != "Dot" else max(c["dot_size"], t)
            rects.append(QRect(cx - d // 2, cy - d // 2, d, d))

        # Outline pass, then fill pass (so overlaps look clean)
        if o:
            p.setPen(Qt.NoPen)
            p.setBrush(ocolor)
            for r in rects:
                p.drawRect(r.adjusted(-o, -o, o, o))
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        for r in rects:
            p.drawRect(r)

        if style == "Circle":
            p.setRenderHint(QPainter.Antialiasing, True)
            p.setBrush(Qt.NoBrush)
            if o:
                p.setPen(QPen(ocolor, t + 2 * o))
                p.drawEllipse(cx - s, cy - s, 2 * s, 2 * s)
            p.setPen(QPen(color, t))
            p.drawEllipse(cx - s, cy - s, 2 * s, 2 * s)
        p.end()


# --------------------------------------------------------------------------
# Settings dialog
# --------------------------------------------------------------------------
class ColorButton(QPushButton):
    changed = pyqtSignal(str)

    def __init__(self, color):
        super().__init__()
        self.color = color
        self.setFixedWidth(70)
        self._refresh()
        self.clicked.connect(self._pick)

    def _refresh(self):
        self.setStyleSheet(
            f"background-color: {self.color}; border: 1px solid #666; height: 20px;"
        )

    def _pick(self):
        chosen = QColorDialog.getColor(QColor(self.color), self, "Pick colour")
        if chosen.isValid():
            self.color = chosen.name()
            self._refresh()
            self.changed.emit(self.color)


class SettingsDialog(QDialog):
    def __init__(self, cfg, overlay):
        super().__init__()
        self.cfg = cfg
        self.overlay = overlay
        self.setWindowTitle("Crosshair Settings")
        self.setMinimumWidth(320)

        form = QFormLayout()

        self.style = QComboBox()
        self.style.addItems(STYLES)
        self.style.setCurrentText(cfg["style"])
        self.style.currentTextChanged.connect(lambda v: self.set("style", v))
        form.addRow("Style", self.style)

        self.color = ColorButton(cfg["color"])
        self.color.changed.connect(lambda v: self.set("color", v))
        form.addRow("Colour", self.color)

        self.size = self._spin("size", 1, 150)
        form.addRow("Size", self.size)
        self.thick = self._spin("thickness", 1, 30)
        form.addRow("Thickness", self.thick)
        self.gap = self._spin("gap", 0, 100)
        form.addRow("Gap", self.gap)

        self.dot_chk = QCheckBox("Centre dot")
        self.dot_chk.setChecked(cfg["center_dot"])
        self.dot_chk.toggled.connect(lambda v: self.set("center_dot", v))
        form.addRow(self.dot_chk)
        self.dot_size = self._spin("dot_size", 1, 30)
        form.addRow("Dot size", self.dot_size)

        self.out_chk = QCheckBox("Outline")
        self.out_chk.setChecked(cfg["outline"])
        self.out_chk.toggled.connect(lambda v: self.set("outline", v))
        form.addRow(self.out_chk)
        self.out_color = ColorButton(cfg["outline_color"])
        self.out_color.changed.connect(lambda v: self.set("outline_color", v))
        form.addRow("Outline colour", self.out_color)
        self.out_thick = self._spin("outline_thickness", 1, 10)
        form.addRow("Outline width", self.out_thick)

        self.opacity = QSlider(Qt.Horizontal)
        self.opacity.setRange(10, 100)
        self.opacity.setValue(cfg["opacity"])
        self.opacity.valueChanged.connect(lambda v: self.set("opacity", v))
        form.addRow("Opacity", self.opacity)

        self.screen = QComboBox()
        for i, s in enumerate(QApplication.screens()):
            self.screen.addItem(f"Screen {i + 1}  ({s.geometry().width()}x{s.geometry().height()})")
        self.screen.setCurrentIndex(min(cfg["screen"], self.screen.count() - 1))
        self.screen.currentIndexChanged.connect(lambda v: self.set("screen", v))
        form.addRow("Monitor", self.screen)

        self.off_x = self._spin("offset_x", -1000, 1000)
        form.addRow("Offset X", self.off_x)
        self.off_y = self._spin("offset_y", -1000, 1000)
        form.addRow("Offset Y", self.off_y)

        reset = QPushButton("Reset to defaults")
        reset.clicked.connect(self.reset)
        close = QPushButton("Close")
        close.clicked.connect(self.close)
        buttons = QHBoxLayout()
        buttons.addWidget(reset)
        buttons.addStretch()
        buttons.addWidget(close)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(QLabel("Hotkey: Ctrl+Alt+C (needs pynput) \u2022 or use the tray icon"))
        layout.addLayout(buttons)

    def _spin(self, key, lo, hi):
        sb = QSpinBox()
        sb.setRange(lo, hi)
        sb.setValue(self.cfg[key])
        sb.valueChanged.connect(lambda v: self.set(key, v))
        return sb

    def set(self, key, value):
        self.cfg[key] = value
        self.overlay.apply()
        save_config(self.cfg)

    def reset(self):
        visible = self.cfg["visible"]
        self.cfg.clear()
        self.cfg.update(DEFAULTS)
        self.cfg["visible"] = visible
        self.overlay.apply()
        save_config(self.cfg)
        self.close()  # reopen to refresh widgets


# --------------------------------------------------------------------------
# App / tray
# --------------------------------------------------------------------------
class HotkeyBridge(QObject):
    toggle = pyqtSignal()


def make_tray_icon():
    pm = QPixmap(32, 32)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setPen(QPen(QColor("#00ff00"), 3))
    p.drawLine(16, 3, 16, 12)
    p.drawLine(16, 20, 16, 29)
    p.drawLine(3, 16, 12, 16)
    p.drawLine(20, 16, 29, 16)
    p.end()
    return QIcon(pm)


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    cfg = load_config()
    overlay = Overlay(cfg)
    dialog_holder = {"dlg": None}

    def open_settings():
        dlg = SettingsDialog(cfg, overlay)
        dialog_holder["dlg"] = dlg  # keep a reference
        dlg.show()
        dlg.raise_()
        dlg.activateWindow()

    # Tray icon
    tray = QSystemTrayIcon(make_tray_icon(), app)
    menu = QMenu()
    act_toggle = QAction("Show / Hide", menu)
    act_toggle.triggered.connect(overlay.toggle)
    act_settings = QAction("Settings\u2026", menu)
    act_settings.triggered.connect(open_settings)
    act_quit = QAction("Quit", menu)
    act_quit.triggered.connect(app.quit)
    for a in (act_toggle, act_settings, act_quit):
        menu.addAction(a)
    tray.setContextMenu(menu)
    tray.setToolTip("Crosshair Overlay")
    tray.activated.connect(
        lambda reason: overlay.toggle() if reason == QSystemTrayIcon.Trigger else None
    )
    tray.show()

    # No tray available (some Linux setups) -> open settings so it's controllable
    if not QSystemTrayIcon.isSystemTrayAvailable():
        open_settings()

    # Optional global hotkey
    bridge = HotkeyBridge()
    bridge.toggle.connect(overlay.toggle)
    try:
        from pynput import keyboard
        hotkeys = keyboard.GlobalHotKeys({"<ctrl>+<alt>+c": bridge.toggle.emit})
        hotkeys.daemon = True
        hotkeys.start()
    except Exception:
        print("pynput not available: global hotkey disabled (tray menu still works).")

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
