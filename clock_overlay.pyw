"""
Modern Transparent Clock Overlay for Windows 11
- Always on top, click-through background
- Drag the clock text to reposition
- Right-click for snap-to-corner menu and exit
- Rename to .pyw to run without a console window
"""

import tkinter as tk
import time


# ── Colour palette ─────────────────────────────────────────────────────────────
BG        = '#010101'   # Near-black used as the transparent key colour
TIME_FG   = '#00D4FF'   # Bright cyan
DATE_FG   = '#5BA8C4'   # Muted blue-grey
SEP_FG    = '#1A4A5A'   # Very dim for the colon separators
MENU_BG   = '#0D1117'
MENU_FG   = '#C9D1D9'
MENU_SEL  = '#00D4FF'
MENU_SELF = '#000000'


class ClockOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self._dx = 0
        self._dy = 0
        self._blink = True  # colon blink state
        self._setup_window()
        self._build_ui()
        self._tick()
        self.root.mainloop()

    # ── Window setup ───────────────────────────────────────────────────────────
    def _setup_window(self):
        r = self.root
        r.overrideredirect(True)          # no title bar / border
        r.attributes('-topmost', True)    # always on top
        r.configure(bg=BG)
        r.attributes('-transparentcolor', BG)   # BG pixels are invisible + click-through

        # Start in top-right corner
        r.update_idletasks()
        sw = r.winfo_screenwidth()
        r.geometry(f'+{sw - 340}+30')

    # ── UI construction ────────────────────────────────────────────────────────
    def _build_ui(self):
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(padx=12, pady=6)

        # ── Time row ──────────────────────────────────────────────────────────
        time_row = tk.Frame(outer, bg=BG)
        time_row.pack()

        hour_font   = ('Segoe UI Light', 54)
        colon_font  = ('Segoe UI Light', 48)
        small_font  = ('Segoe UI Light', 32)
        ampm_font   = ('Segoe UI', 14)

        self.lbl_hh   = self._lbl(time_row, '00', hour_font,  TIME_FG)
        self.lbl_c1   = self._lbl(time_row, ':',  colon_font, TIME_FG)
        self.lbl_mm   = self._lbl(time_row, '00', hour_font,  TIME_FG)
        self.lbl_c2   = self._lbl(time_row, ':',  colon_font, SEP_FG)
        self.lbl_ss   = self._lbl(time_row, '00', small_font, DATE_FG)
        self.lbl_ampm = self._lbl(time_row, 'AM', ampm_font,  DATE_FG,
                                  padx=6, pady=(18, 0))

        # Pack the row components
        for w in (self.lbl_hh, self.lbl_c1, self.lbl_mm,
                  self.lbl_c2, self.lbl_ss, self.lbl_ampm):
            w.pack(side='left')

        # ── Date row ──────────────────────────────────────────────────────────
        self.lbl_date = tk.Label(
            outer, text='', font=('Segoe UI', 12), fg=DATE_FG, bg=BG,
        )
        self.lbl_date.pack(pady=(0, 2))

        # ── Bind interactions ─────────────────────────────────────────────────
        for widget in self.root.winfo_children():
            self._bind_all(widget)

    def _lbl(self, parent, text, font, fg, padx=0, pady=0):
        lbl = tk.Label(parent, text=text, font=font, fg=fg, bg=BG,
                       padx=padx, pady=pady)
        return lbl

    def _bind_all(self, widget):
        widget.bind('<ButtonPress-1>', self._on_press)
        widget.bind('<B1-Motion>',     self._on_drag)
        widget.bind('<Button-3>',      self._show_menu)
        for child in widget.winfo_children():
            self._bind_all(child)

    # ── Clock tick ─────────────────────────────────────────────────────────────
    def _tick(self):
        now = time.localtime()
        h24 = now.tm_hour
        m   = now.tm_min
        s   = now.tm_sec

        h12 = h24 % 12 or 12
        ampm = 'AM' if h24 < 12 else 'PM'

        self.lbl_hh['text']   = f'{h12:02d}'
        self.lbl_mm['text']   = f'{m:02d}'
        self.lbl_ss['text']   = f'{s:02d}'
        self.lbl_ampm['text'] = ampm

        # Blinking colon on the hour:minute separator
        self._blink = not self._blink
        self.lbl_c1['fg'] = TIME_FG if self._blink else SEP_FG

        self.lbl_date['text'] = time.strftime('%A  ·  %B %d, %Y', now)

        self.root.after(1000, self._tick)

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
        m.add_command(label='  Snap  ↗  Top Right',    command=lambda: self._snap('tr'))
        m.add_command(label='  Snap  ↖  Top Left',     command=lambda: self._snap('tl'))
        m.add_command(label='  Snap  ↘  Bottom Right', command=lambda: self._snap('br'))
        m.add_command(label='  Snap  ↙  Bottom Left',  command=lambda: self._snap('bl'))
        m.add_separator()
        m.add_command(label='  ✕  Exit Clock',         command=self.root.destroy)
        m.tk_popup(event.x_root, event.y_root)

    def _snap(self, corner: str):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w  = self.root.winfo_width()
        h  = self.root.winfo_height()
        pad, taskbar = 24, 52
        positions = {
            'tr': (sw - w - pad,       pad),
            'tl': (pad,                pad),
            'br': (sw - w - pad,       sh - h - taskbar),
            'bl': (pad,                sh - h - taskbar),
        }
        x, y = positions[corner]
        self.root.geometry(f'+{x}+{y}')


if __name__ == '__main__':
    ClockOverlay()
