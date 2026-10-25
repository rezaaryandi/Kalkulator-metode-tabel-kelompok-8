"""Titik masuk aplikasi. Jalankan:  python main.py"""
import sys

from aplikasi import KalkulatorMetodeTabel

if __name__ == "__main__":
    if sys.platform == "win32":                       # anti-buram di Windows (High-DPI)
        from ctypes import windll
        try:
            windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            windll.user32.SetProcessDPIAware()
    KalkulatorMetodeTabel().mainloop()
