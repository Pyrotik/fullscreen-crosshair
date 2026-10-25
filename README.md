# Fullscreen Crosshair Overlay

A lightweight fullscreen crosshair overlay for Linux.

Works over fullscreen applications and games — perfect when you need a permanent aiming reference.

## 🚀 v2.0.0 — Now Written in Rust!
This project was originally built in Python & PyQt5. It has now been completely rewritten in **Rust** for better performance, lower memory usage, and a smaller binary. 

* **Download the new Rust version:** Check the [Latest Release](https://github.com/Pyrotik/fullscreen-crosshair/releases/latest).
* **Looking for the old Python version?** The original Python source and binary are still available in the [v1.x Releases](https://github.com/Pyrotik/fullscreen-crosshair/releases).

## Download

Download the latest release: https://github.com/Pyrotik/fullscreen-crosshair/releases/latest

File | Description  
---|---  
crosshair-rs-linux-x86_64 | Standalone binary (Rust version). No installation is required.  
fullscreen-crosshair-rs.tar.gz | Compressed archive (Rust version).  

## Usage

    chmod +x crosshair-rs-linux-x86_64
    ./crosshair-rs-linux-x86_64

## Requirements

  * Linux (tested on CachyOS)
  * X11 or Wayland desktop environment

## Built from Source

For the old Python version, the source code is in `crosshair.py`. To run it:

Install dependencies (Arch/CachyOS):
    sudo pacman -S python python-pyqt5

Or Debian/Ubuntu:
    sudo apt install python3 python3-pyqt5

Run it:
    python3 crosshair.py

## Built With AI Assistance

* **Original Python Version:** Created with help from DeepSeek and Claude.
* **Rust Rewrite:** Created with help from Grok Bot, Claude, and DeepSeek.

## License

MIT — free to use, modify, and share.
