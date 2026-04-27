"""
Modern Transparent Clock Overlay for Windows 11
- No console window — run via shortcut using pythonw.exe
- System tray icon for all controls
- Transparent, always-on-top, click-through background
- Drag clock text to reposition; right-click for quick access
"""

import tkinter as tk
from tkinter import colorchooser
import time
import threading
import math
import pystray
from PIL import Image, ImageDraw


# ── Colour palette ─────────────────────────────────────────────────────────────
BG        = '#010101'   # Key colour — made fully transparent by Windows
TIME_FG   = '#00D4FF'   # Default: bright cyan
MENU_BG   = '#0D1117'
MENU_FG   = '#C9D1D9'
MENU_SEL  = '#00D4FF'
MENU_SELF = '#000000'


def _dim(hex_color: str, factor: float = 0.45) -> str:
    """Return a dimmed version of a hex colour for secondary elements."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return f'#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}'


def _make_tray_icon(color: str = '#00D4FF') -> Image.Image:
    """Draw a clock-face icon for the system tray in the given colour."""
    size = 64
    img  = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2
    r = size // 2 - 4
    cr, cg, cb = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    rgba = (cr, cg, cb, 255)

    # Outer ring
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=rgba, width=4)

    # Hour hand  (~10 o'clock)
    for angle, length, width in [(-60, r * 0.50, 4), (60, r * 0.70, 3)]:
        rad = math.radians(angle)
        x2  = cx + length * math.sin(rad)
        y2  = cy - length * math.cos(rad)
        draw.line([cx, cy, x2, y2], fill=rgba, width=width)

    # Centre dot
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=rgba)

    return img


class ClockOverlay:
    def __init__(self):
        self.root          = tk.Tk()
        self._dx           = 0
        self._dy           = 0
        self._blink        = True
        self._time_color   = TIME_FG
        self._tray         = None

        self._setup_window()
        self._build_ui()
        self._tick()
        self._start_tray()
        self.root.mainloop()

    # ── Window ─────────────────────────────────────────────────────────────────
    def _setup_window(self):
        r = self.root
        r.overrideredirect(True)
        r.attributes('-topmost', True)
        r.configure(bg=BG)
        r.attributes('-transparentcolor', BG)
        r.update_idletasks()
        sw = r.winfo_screenwidth()
        r.geometry(f'+{sw - 340}+30')

    # ── UI ─────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        outer    = tk.Frame(self.root, bg=BG)
        outer.pack(padx=12, pady=6)
        time_row = tk.Frame(outer, bg=BG)
        time_row.pack()

        c, d = self._time_color, _dim(self._time_color)

        self.lbl_hh   = self._lbl(time_row, '00', ('Segoe UI Light', 54), c)
        self.lbl_c1   = self._lbl(time_row, ':',  ('Segoe UI Light', 48), c)
        self.lbl_mm   = self._lbl(time_row, '00', ('Segoe UI Light', 54), c)
        self.lbl_c2   = self._lbl(time_row, ':',  ('Segoe UI Light', 48), d)
        self.lbl_ss   = self._lbl(time_row, '00', ('Segoe UI Light', 32), d)
        self.lbl_ampm = self._lbl(time_row, 'AM', ('Segoe UI', 14),       d, padx=6)

        for w in (self.lbl_hh, self.lbl_c1, self.lbl_mm, self.lbl_c2, self.lbl_ss):
            w.pack(side='left')
        self.lbl_ampm.pack(side='left', anchor='s', pady=(0, 8))

        self.lbl_date = tk.Label(
            outer, text='', font=('Segoe UI', 12),
            fg=_dim(self._time_color, 0.65), bg=BG,
        )
        self.lbl_date.pack(pady=(0, 2))

        for widget in self.root.winfo_children():
            self._bind_all(widget)

    def _lbl(self, parent, text, font, fg, padx=0, pady=0):
        return tk.Label(parent, text=text, font=font, fg=fg, bg=BG,
                        padx=padx, pady=pady)

    def _bind_all(self, widget):
        widget.bind('<ButtonPress-1>', self._on_press)
        widget.bind('<B1-Motion>',     self._on_drag)
        widget.bind('<Button-3>',      self._show_menu)
        for child in widget.winfo_children():
            self._bind_all(child)

    # ── Tick ───────────────────────────────────────────────────────────────────
    def _tick(self):
        now  = time.localtime()
        h24  = now.tm_hour
        h12  = h24 % 12 or 12
        ampm = 'AM' if h24 < 12 else 'PM'

        self.lbl_hh['text']   = f'{h12:02d}'
        self.lbl_mm['text']   = f'{now.tm_min:02d}'
        self.lbl_ss['text']   = f'{now.tm_sec:02d}'
        self.lbl_ampm['text'] = ampm

        self._blink   = not self._blink
        self.lbl_c1['fg'] = self._time_color if self._blink else _dim(self._time_color)
        self.lbl_date['text'] = time.strftime('%A  ·  %B %d, %Y', now)

        self.root.after(1000, self._tick)

    # ── Colour ─────────────────────────────────────────────────────────────────
    def _apply_color(self, color: str):
        self._time_color   = color
        dim                = _dim(color)
        dim2               = _dim(color, 0.65)
        self.lbl_hh['fg']   = color
        self.lbl_c1['fg']   = color
        self.lbl_mm['fg']   = color
        self.lbl_c2['fg']   = dim
        self.lbl_ss['fg']   = dim
        self.lbl_ampm['fg'] = dim
        self.lbl_date['fg'] = dim2
        if self._tray:
            self._tray.icon = _make_tray_icon(color)

    def _pick_color_dialog(self):
        result = colorchooser.askcolor(
            color=self._time_color,
            title='Choose Clock Color',
            parent=self.root,
        )
        if result and result[1]:
            self._apply_color(result[1])

    # ── Drag ───────────────────────────────────────────────────────────────────
    def _on_press(self, event):
        self._dx = event.x_root - self.root.winfo_x()
        self._dy = event.y_root - self.root.winfo_y()

    def _on_drag(self, event):
        self.root.geometry(f'+{event.x_root - self._dx}+{event.y_root - self._dy}')

    # ── Right-click menu (on the clock itself) ─────────────────────────────────
    def _show_menu(self, event):
        m = tk.Menu(self.root, tearoff=0,
                    bg=MENU_BG, fg=MENU_FG,
                    activebackground=MENU_SEL,
                    activeforeground=MENU_SELF,
                    relief='flat', bd=1)
        m.add_command(label='  Color  ●  Cyan (default)', command=lambda: self._apply_color('#00D4FF'))
        m.add_command(label='  Color  ●  White',          command=lambda: self._apply_color('#FFFFFF'))
        m.add_command(label='  Color  ●  Soft Green',     command=lambda: self._apply_color('#00FF99'))
        m.add_command(label='  Color  ●  Warm Orange',    command=lambda: self._apply_color('#FF8C42'))
        m.add_command(label='  Color  ●  Purple',         command=lambda: self._apply_color('#CC88FF'))
        m.add_command(label='  Color  ●  Pink',           command=lambda: self._apply_color('#FF6EB4'))
        m.add_command(label='  Color  ⊕  Custom...',      command=self._pick_color_dialog)
        m.add_separator()
        m.add_command(label='  Snap  ↗  Top Right',    command=lambda: self._snap('tr'))
        m.add_command(label='  Snap  ↖  Top Left',     command=lambda: self._snap('tl'))
        m.add_command(label='  Snap  ↘  Bottom Right', command=lambda: self._snap('br'))
        m.add_command(label='  Snap  ↙  Bottom Left',  command=lambda: self._snap('bl'))
        m.add_separator()
        m.add_command(label='  ✕  Exit Clock', command=self._exit)
        m.tk_popup(event.x_root, event.y_root)

    # ── Snap ───────────────────────────────────────────────────────────────────
    def _snap(self, corner: str):
        self.root.update_idletasks()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        w,  h  = self.root.winfo_width(),       self.root.winfo_height()
        pad, taskbar = 24, 52
        positions = {
            'tr': (sw - w - pad,  pad),
            'tl': (pad,           pad),
            'br': (sw - w - pad,  sh - h - taskbar),
            'bl': (pad,           sh - h - taskbar),
        }
        x, y = positions[corner]
        self.root.geometry(f'+{x}+{y}')

    # ── System tray ────────────────────────────────────────────────────────────
    def _start_tray(self):
        def _set(c):
            return lambda icon, item: self.root.after(0, lambda: self._apply_color(c))

        def _snap_item(corner):
            return lambda icon, item: self.root.after(0, lambda: self._snap(corner))

        def _custom(icon, item):
            self.root.after(0, self._pick_color_dialog)

        def _exit(icon, item):
            icon.stop()
            self.root.after(0, self.root.destroy)

        menu = pystray.Menu(
            pystray.MenuItem('Color', pystray.Menu(
                pystray.MenuItem('Cyan (default)', _set('#00D4FF')),
                pystray.MenuItem('White',          _set('#FFFFFF')),
                pystray.MenuItem('Soft Green',     _set('#00FF99')),
                pystray.MenuItem('Warm Orange',    _set('#FF8C42')),
                pystray.MenuItem('Purple',         _set('#CC88FF')),
                pystray.MenuItem('Pink',           _set('#FF6EB4')),
                pystray.MenuItem('Custom...',      _custom),
            )),
            pystray.MenuItem('Snap to Corner', pystray.Menu(
                pystray.MenuItem('Top Right',    _snap_item('tr')),
                pystray.MenuItem('Top Left',     _snap_item('tl')),
                pystray.MenuItem('Bottom Right', _snap_item('br')),
                pystray.MenuItem('Bottom Left',  _snap_item('bl')),
            )),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Exit', _exit, default=True),
        )

        def _run():
            self._tray = pystray.Icon(
                'clock_overlay',
                _make_tray_icon(self._time_color),
                'Clock Overlay',
                menu,
            )
            self._tray.run()

        threading.Thread(target=_run, daemon=True).start()

    def _exit(self):
        if self._tray:
            self._tray.stop()
        self.root.destroy()


if __name__ == '__main__':
    ClockOverlay()
