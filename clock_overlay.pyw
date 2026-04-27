"""
Modern Transparent Clock Overlay for Windows 11
- Always on top, click-through background
- Drag the clock text to reposition
- Right-click for snap-to-corner, color picker, and exit
"""

import tkinter as tk
from tkinter import colorchooser
import time


# ── Colour palette ─────────────────────────────────────────────────────────────
BG        = '#010101'   # Key colour — made fully transparent by Windows
TIME_FG   = '#00D4FF'   # Default: bright cyan  (user can change via right-click)
MENU_BG   = '#0D1117'
MENU_FG   = '#C9D1D9'
MENU_SEL  = '#00D4FF'
MENU_SELF = '#000000'


def _dim(hex_color: str, factor: float = 0.45) -> str:
    """Return a darker/dimmer version of a hex colour for secondary elements."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return f'#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}'


class ClockOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self._dx       = 0
        self._dy       = 0
        self._blink    = True
        self._time_color = TIME_FG          # mutable — changed by color picker
        self._setup_window()
        self._build_ui()
        self._tick()
        self.root.mainloop()

    # ── Window setup ───────────────────────────────────────────────────────────
    def _setup_window(self):
        r = self.root
        r.overrideredirect(True)
        r.attributes('-topmost', True)
        r.configure(bg=BG)
        r.attributes('-transparentcolor', BG)   # BG pixels: invisible + click-through

        # Start in top-right corner
        r.update_idletasks()
        sw = r.winfo_screenwidth()
        r.geometry(f'+{sw - 340}+30')

    # ── UI construction ────────────────────────────────────────────────────────
    def _build_ui(self):
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(padx=12, pady=6)

        time_row = tk.Frame(outer, bg=BG)
        time_row.pack()

        hour_font  = ('Segoe UI Light', 54)
        colon_font = ('Segoe UI Light', 48)
        small_font = ('Segoe UI Light', 32)
        ampm_font  = ('Segoe UI', 14)

        c = self._time_color
        d = _dim(c)

        self.lbl_hh   = self._lbl(time_row, '00', hour_font,  c)
        self.lbl_c1   = self._lbl(time_row, ':',  colon_font, c)
        self.lbl_mm   = self._lbl(time_row, '00', hour_font,  c)
        self.lbl_c2   = self._lbl(time_row, ':',  colon_font, d)
        self.lbl_ss   = self._lbl(time_row, '00', small_font, d)
        self.lbl_ampm = self._lbl(time_row, 'AM', ampm_font,  d, padx=6)

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

    # ── Clock tick ─────────────────────────────────────────────────────────────
    def _tick(self):
        now  = time.localtime()
        h24  = now.tm_hour
        h12  = h24 % 12 or 12
        ampm = 'AM' if h24 < 12 else 'PM'

        self.lbl_hh['text']   = f'{h12:02d}'
        self.lbl_mm['text']   = f'{now.tm_min:02d}'
        self.lbl_ss['text']   = f'{now.tm_sec:02d}'
        self.lbl_ampm['text'] = ampm

        self._blink = not self._blink
        self.lbl_c1['fg'] = self._time_color if self._blink else _dim(self._time_color)

        self.lbl_date['text'] = time.strftime('%A  ·  %B %d, %Y', now)

        self.root.after(1000, self._tick)

    # ── Apply a new time colour to every relevant widget ──────────────────────
    def _apply_color(self, color: str):
        self._time_color = color
        dim  = _dim(color)
        dim2 = _dim(color, 0.65)

        self.lbl_hh['fg']   = color
        self.lbl_c1['fg']   = color
        self.lbl_mm['fg']   = color
        self.lbl_c2['fg']   = dim
        self.lbl_ss['fg']   = dim
        self.lbl_ampm['fg'] = dim
        self.lbl_date['fg'] = dim2

    # ── Drag ───────────────────────────────────────────────────────────────────
    def _on_press(self, event):
        self._dx = event.x_root - self.root.winfo_x()
        self._dy = event.y_root - self.root.winfo_y()

    def _on_drag(self, event):
        self.root.geometry(f'+{event.x_root - self._dx}+{event.y_root - self._dy}')

    # ── Right-click menu ───────────────────────────────────────────────────────
    def _show_menu(self, event):
        m = tk.Menu(self.root, tearoff=0,
                    bg=MENU_BG, fg=MENU_FG,
                    activebackground=MENU_SEL,
                    activeforeground=MENU_SELF,
                    relief='flat', bd=1)

        # Colour presets
        m.add_command(label='  Color  ●  Cyan (default)', command=lambda: self._apply_color('#00D4FF'))
        m.add_command(label='  Color  ●  White',          command=lambda: self._apply_color('#FFFFFF'))
        m.add_command(label='  Color  ●  Soft Green',     command=lambda: self._apply_color('#00FF99'))
        m.add_command(label='  Color  ●  Warm Orange',    command=lambda: self._apply_color('#FF8C42'))
        m.add_command(label='  Color  ●  Purple',         command=lambda: self._apply_color('#CC88FF'))
        m.add_command(label='  Color  ●  Pink',           command=lambda: self._apply_color('#FF6EB4'))
        m.add_command(label='  Color  ⊕  Custom...',      command=self._pick_color)
        m.add_separator()

        # Snap positions
        m.add_command(label='  Snap  ↗  Top Right',    command=lambda: self._snap('tr'))
        m.add_command(label='  Snap  ↖  Top Left',     command=lambda: self._snap('tl'))
        m.add_command(label='  Snap  ↘  Bottom Right', command=lambda: self._snap('br'))
        m.add_command(label='  Snap  ↙  Bottom Left',  command=lambda: self._snap('bl'))
        m.add_separator()

        m.add_command(label='  ✕  Exit Clock', command=self.root.destroy)
        m.tk_popup(event.x_root, event.y_root)

    def _pick_color(self):
        result = colorchooser.askcolor(
            color=self._time_color,
            title='Choose Clock Color',
            parent=self.root,
        )
        if result and result[1]:        # result[1] is the hex string, None if cancelled
            self._apply_color(result[1])

    def _snap(self, corner: str):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w  = self.root.winfo_width()
        h  = self.root.winfo_height()
        pad, taskbar = 24, 52
        positions = {
            'tr': (sw - w - pad,  pad),
            'tl': (pad,           pad),
            'br': (sw - w - pad,  sh - h - taskbar),
            'bl': (pad,           sh - h - taskbar),
        }
        x, y = positions[corner]
        self.root.geometry(f'+{x}+{y}')


if __name__ == '__main__':
    ClockOverlay()
