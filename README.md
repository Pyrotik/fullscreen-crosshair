# Fullscreen Crosshair Overlay

A lightweight fullscreen crosshair overlay for Linux, built with Python and PyQt5.

Works over fullscreen applications and games — perfect when you need a permanent aiming reference.

## Download

Download the latest release:
https://github.com/Pyrotik/fullscreen-crosshair/releases/latest

| File | Description |
|------|-------------|
| crosshair-linux | Standalone binary. Python and PyQt5 are bundled inside, so no installation is required. |

## Usage

    chmod +x crosshair-linux
    ./crosshair-linux

## Requirements

- Linux (tested on CachyOS)
- X11 or Wayland desktop environment

## Built from Source

The source code is in crosshair.py. To run it yourself instead of the prebuilt binary:

Install dependencies (Arch/CachyOS):

    sudo pacman -S python python-pyqt5

Or Debian/Ubuntu:

    sudo apt install python3 python3-pyqt5

Run it:

    python3 crosshair.py

## Built With AI Assistance

This project was created with help from DeepSeek and Claude.

## License

MIT — free to use, modify, and share.
