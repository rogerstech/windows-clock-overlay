# Windows 11 Clock Overlay

A modern, transparent always-on-top clock overlay for Windows 11. The background is fully invisible and click-through — only the glowing clock text floats above your other apps. Controlled entirely through a system tray icon; no console window.

---

## Features

- Always on top of all windows
- Transparent, click-through background
- System tray icon for all controls — no console window
- Color presets + full custom color picker
- Drag to reposition anywhere on screen
- Right-click the clock for quick access to all options
- Snap to any corner of the screen
- Blinking colon separator
- Shows time (12-hour) and full date

---

## Prerequisites

### 1 — Python 3.12

> **Python 3.14+ has a known tkinter bug that prevents the window from opening. You must use Python 3.12.**

1. Download: https://www.python.org/downloads/release/python-3129/
   - Choose **Windows installer (64-bit)**
2. Run the installer and make sure these are checked:
   - **"Add Python 3.12 to PATH"**
   - Under **Customize installation → Optional Features**: `tcl/tk and IDLE`
3. Complete the installation

Verify by opening **Command Prompt** and running:
```
py -3.12 --version
```
You should see `Python 3.12.x`.

### 2 — Python dependencies

Open **Command Prompt** and run:
```
py -3.12 -m pip install pystray pillow
```

- `pystray` — powers the system tray icon
- `pillow` — draws the clock icon image in the tray

---

## Running the Clock

### From Command Prompt (with console window)
```
py -3.12 clock_overlay.pyw
```

### Without a console window (recommended)
Use `pythonw.exe` instead of `python.exe`:
```
C:\Users\YourName\AppData\Local\Programs\Python\Python312\pythonw.exe "C:\Path\To\clock_overlay.pyw"
```

Or just double-click `clock_overlay.pyw` if `.pyw` files are associated with `pythonw.exe`.

The clock appears in the top-right of your screen. A tray icon appears in the system tray (bottom-right of taskbar).

---

## Creating a No-Console Startup Shortcut

### Step 1 — Find pythonw.exe

Open **Command Prompt** and run:
```
py -3.12 -c "import sys, os; print(os.path.join(os.path.dirname(sys.executable), 'pythonw.exe'))"
```
Copy the path it prints (e.g. `C:\Users\YourName\AppData\Local\Programs\Python\Python312\pythonw.exe`).

### Step 2 — Create the shortcut

1. Right-click your Desktop → **New → Shortcut**
2. In the **location** field enter (replace both paths with your actual paths):
   ```
   "C:\Users\YourName\AppData\Local\Programs\Python\Python312\pythonw.exe" "C:\Path\To\clock_overlay.pyw"
   ```
3. Name it **Clock Overlay** and click **Finish**
4. Right-click the shortcut → **Properties** → set **Run** to **Minimized**
5. Click **OK**

### Step 3 — Add to Windows startup

1. Press **Win + R**, type `shell:startup`, press **Enter**
2. Move or paste the shortcut into that folder

The clock will now launch silently every time you log in — no console window, just the tray icon and the overlay.

---

## Usage

| Action | Result |
|---|---|
| Drag the clock text | Move it anywhere on screen |
| Right-click the clock | Quick menu: colors, snap, exit |
| System tray icon | Full menu: colors, snap, exit |
| Double-click tray icon | Exit |
| Click background area | Passes through to the app behind |

---

## Troubleshooting

**`py -3.12` gives errno 2**
Run `py --list` to confirm Python 3.12 is installed. If not, re-run the installer.

**`ModuleNotFoundError: pystray` or `pillow`**
Run `py -3.12 -m pip install pystray pillow` and try again.

**Clock opens but no tray icon appears**
Make sure `pystray` installed successfully. Check the taskbar overflow (the `^` arrow on the right of the taskbar).

**Window appears but is not transparent**
Ensure hardware acceleration is enabled and GPU drivers are up to date.
