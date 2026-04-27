# Windows 11 Clock Overlay

A modern, transparent always-on-top clock overlay for Windows 11. The background is fully invisible and click-through — only the glowing clock text floats above your other apps.

![Clock showing HH:MM:SS with date below in cyan on a transparent background]

---

## Features

- Always on top of all windows
- Transparent, click-through background
- Drag to reposition anywhere on screen
- Right-click to snap to any corner or exit
- Blinking colon separator
- Shows time (12-hour) and full date

---

## Prerequisites

### Python 3.12 (required)

> **Python 3.14+ has a known tkinter bug that prevents the window from opening. You must use Python 3.12.**

1. Download the installer: https://www.python.org/downloads/release/python-3129/
   - Choose **Windows installer (64-bit)**
2. Run the installer and make sure the following are checked:
   - **"Add Python 3.12 to PATH"**
   - Under **Customize installation → Optional Features**: `tcl/tk and IDLE`
3. Complete the installation

### Verify the install

Open **Command Prompt** and run:

```
py -3.12 --version
```

You should see `Python 3.12.x`. If you get an error, re-run the installer and ensure tcl/tk is selected.

---

## Running the Clock

Open **Command Prompt**, navigate to the folder, and run:

```
py -3.12 clock_overlay.pyw
```

The clock will appear in the top-right area of your screen. You can drag it anywhere or right-click for corner snap options.

---

## Creating a Startup Shortcut

To have the clock launch automatically when Windows starts (without a Command Prompt window):

### Step 1 — Create a shortcut

1. Right-click `clock_overlay.pyw` → **Create shortcut**
2. Right-click the new shortcut → **Properties**
3. In the **Target** field, replace whatever is there with:
   ```
   C:\Windows\py.exe -3.12 "C:\Your\Path\To\clock_overlay.pyw"
   ```
   Replace `C:\Your\Path\To\` with the actual folder path where you saved the file.
4. Set **Run** to **Minimized** (this prevents any brief console flash)
5. Click **OK**

### Step 2 — Add to Windows startup

1. Press **Win + R**, type `shell:startup`, and press Enter
2. This opens your Startup folder in File Explorer
3. Move or paste the shortcut into that folder

The clock will now launch automatically every time you log in to Windows.

---

## Usage

| Action | Result |
|---|---|
| Drag the clock | Move it anywhere on screen |
| Right-click | Open menu: snap to corner or exit |
| Click background area | Passes through to the app behind |

---

## Troubleshooting

**Clock doesn't open / no error shown**
- Make sure you are running with `py -3.12` not just `python` (which may use 3.14+)
- Run `py --list` to confirm Python 3.12 is installed

**`errno 2` when running**
- The file path is wrong or Python 3.12 is not installed
- Run `py --list` to see available versions

**Window appears but is solid dark (not transparent)**
- Transparency requires Windows 11 with hardware acceleration enabled
- Make sure your GPU drivers are up to date
