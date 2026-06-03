# -*- coding: utf-8 -*-
"""
FINDexplorER — Point d'entrée
Interface CustomTkinter + raccourci global Ctrl+Espace + icône barre des tâches
"""
import os
import sys
import socket
import threading
import ctypes
import ctypes.wintypes

if getattr(sys, "frozen", False):
    _HERE = sys._MEIPASS
else:
    _HERE = os.path.dirname(os.path.abspath(__file__))

INSTANCE_PORT = 51209
TOGGLE_MSG = b"TOGGLE"

WM_HOTKEY = 0x0312
MOD_CONTROL = 0x0002
VK_SPACE = 0x20
VK_APPS = 0x5D  # Touche Menu contextuelle
HOTKEY_ID_TOGGLE = 1
HOTKEY_ID_MENU = 2


def _ico_path():
    return os.path.join(_HERE, "FindExplorer.ico")


def notify_running_instance():
    try:
        with socket.create_connection(("127.0.0.1", INSTANCE_PORT), timeout=1.0) as s:
            s.sendall(TOGGLE_MSG)
        return True
    except OSError:
        return False


def _try_bind_instance_port():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind(("127.0.0.1", INSTANCE_PORT))
        srv.listen(4)
        return srv
    except OSError:
        srv.close()
        return None


def _instance_server(srv, on_toggle):
    while True:
        conn, _ = srv.accept()
        with conn:
            try:
                data = conn.recv(64)
                if data.strip() == TOGGLE_MSG:
                    on_toggle()
            except OSError:
                pass


def _hotkey_thread(callback):
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    # Win64 : WPARAM/LPARAM/LRESULT sont 64 bits (sinon OverflowError dans DefWindowProcW)
    if ctypes.sizeof(ctypes.c_void_p) == 8:
        LRESULT = ctypes.c_longlong
        WPARAM_T = ctypes.c_uint64
        LPARAM_T = ctypes.c_longlong
    else:
        LRESULT = ctypes.c_long
        WPARAM_T = ctypes.c_uint32
        LPARAM_T = ctypes.c_long

    user32.DefWindowProcW.argtypes = [
        ctypes.wintypes.HWND,
        ctypes.wintypes.UINT,
        WPARAM_T,
        LPARAM_T,
    ]
    user32.DefWindowProcW.restype = LRESULT

    WNDPROC = ctypes.WINFUNCTYPE(
        LRESULT,
        ctypes.wintypes.HWND,
        ctypes.wintypes.UINT,
        WPARAM_T,
        LPARAM_T,
    )

    def wnd_proc(hwnd, msg, wp, lp):
        if msg == WM_HOTKEY and wp == HOTKEY_ID_TOGGLE:
            threading.Thread(target=callback, daemon=True).start()
            return 0
        return user32.DefWindowProcW(hwnd, msg, wp, lp)

    cb = WNDPROC(wnd_proc)

    class WNDCLASSEXW(ctypes.Structure):
        _fields_ = [
            ("cbSize", ctypes.c_uint),
            ("style", ctypes.c_uint),
            ("lpfnWndProc", WNDPROC),
            ("cbClsExtra", ctypes.c_int),
            ("cbWndExtra", ctypes.c_int),
            ("hInstance", ctypes.wintypes.HANDLE),
            ("hIcon", ctypes.wintypes.HANDLE),
            ("hCursor", ctypes.wintypes.HANDLE),
            ("hbrBackground", ctypes.wintypes.HANDLE),
            ("lpszMenuName", ctypes.wintypes.LPCWSTR),
            ("lpszClassName", ctypes.wintypes.LPCWSTR),
            ("hIconSm", ctypes.wintypes.HANDLE),
        ]

    hinstance = kernel32.GetModuleHandleW(None)
    class_name = "FEHotkey_FINDexplorER"

    wc = WNDCLASSEXW()
    wc.cbSize = ctypes.sizeof(wc)
    wc.lpfnWndProc = cb
    wc.hInstance = hinstance
    wc.lpszClassName = class_name
    user32.RegisterClassExW(ctypes.byref(wc))

    HWND_MESSAGE = ctypes.wintypes.HWND(-3)
    hwnd = user32.CreateWindowExW(
        0, class_name, "FEHotkey", 0, 0, 0, 0, 0,
        HWND_MESSAGE, None, hinstance, None,
    )
    if not hwnd:
        return

    user32.RegisterHotKey(hwnd, HOTKEY_ID_TOGGLE, MOD_CONTROL, VK_SPACE)
    msg = ctypes.wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))


def _schedule_toggle():
    import fe_ui
    app = fe_ui.get_app()
    if app:
        app.after(0, app.toggle_visibility)


def run_tray():
    try:
        import pystray
        from PIL import Image

        ico = _ico_path()
        if os.path.exists(ico):
            img = Image.open(ico).convert("RGBA").resize((64, 64))
        else:
            from PIL import ImageDraw
            img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            d.rectangle([8, 20, 56, 48], fill="#0078D4")
            d.rectangle([10, 22, 54, 46], fill="#2D2D30")

        menu = pystray.Menu(
            pystray.MenuItem(
                "Ouvrir / Fermer  (Ctrl+Espace)",
                lambda _i, _it: _schedule_toggle(),
                default=True,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quitter", lambda icon, _item: (icon.stop(), os._exit(0))),
        )
        icon = pystray.Icon("FINDexplorER", img, "FINDexplorER", menu)
        icon.run()
    except ImportError:
        import time
        while True:
            time.sleep(60)


def main():
    srv = _try_bind_instance_port()
    if srv is None:
        notify_running_instance()
        return

    threading.Thread(
        target=_instance_server,
        args=(srv, _schedule_toggle),
        daemon=True,
    ).start()

    if sys.platform == "win32":
        threading.Thread(target=_hotkey_thread, args=(_schedule_toggle,), daemon=True).start()

    threading.Thread(target=run_tray, daemon=True).start()

    import customtkinter as ctk
    import fe_ui

    ctk.set_appearance_mode("system")
    fe_ui.run_ui()


if __name__ == "__main__":
    main()
