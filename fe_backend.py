# -*- coding: utf-8 -*-
"""FINDexplorER — Logique fichiers et opérations système."""
import os
import re
import sys
import shutil
import subprocess
import ctypes
import urllib.parse
from datetime import datetime

ICONS = {
    "folder": "📁", "drive": "💾", "txt": "📝", "pdf": "📕", "doc": "📘", "docx": "📘",
    "xls": "📗", "xlsx": "📗", "ppt": "📙", "pptx": "📙", "png": "🖼", "jpg": "🖼",
    "jpeg": "🖼", "gif": "🖼", "mp4": "🎬", "mp3": "🎵", "zip": "🗜", "exe": "⚙️",
    "py": "🐍", "html": "🌐", "js": "📜", "json": "📋",
}


def item_icon(it):
    return ICONS.get(it.get("type")) or ICONS.get(
        (it.get("name") or "").split(".")[-1].lower()
    ) or "📄"


def fmt_size(n):
    if not n:
        return "—"
    for u in ("o", "Ko", "Mo", "Go", "To"):
        if n < 1024:
            return f"{n:.0f} {u}" if u == "o" else f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} To"


def fmt_date(ts):
    try:
        return datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M")
    except Exception:
        return "—"


def normalize_path(path):
    path = (path or "").replace("\\", "/")
    if not path:
        return path
    # Chemins réseau : ne pas toucher au double slash
    if path.startswith("//"):
        return path.rstrip("/") or path
    # Racine d'un lecteur (ex: "C:/", "C:", "c:///") → toujours "C:/"
    if re.match(r"^[A-Za-z]:/*$", path):
        return path[0].upper() + ":/"
    # Chemin normal : enlever le slash final
    return path.rstrip("/")


def get_drives():
    drives = []
    if sys.platform != "win32":
        return drives
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for i in range(26):
        if bitmask & (1 << i):
            letter = chr(65 + i) + ":\\"
            try:
                buf = ctypes.create_unicode_buffer(256)
                ctypes.windll.kernel32.GetVolumeInformationW(
                    letter, buf, 256, None, None, None, None, 0
                )
                label = buf.value
            except Exception:
                label = ""
            drives.append({
                "name": f"{letter[:-1]} — {label}" if label else letter[:-1],
                "path": letter.replace("\\", "/"),
                "type": "drive",
                "size": "",
                "date": "",
                "size_b": 0,
                "date_ts": 0,
                "hidden": False,
            })
    return drives


def list_dir(path):
    items = []
    if not path:
        return items
    # Normaliser pour os.scandir : C:/ → C:\ sur Windows
    scan_path = os.path.normpath(path)
    try:
        for e in os.scandir(scan_path):
            try:
                st = e.stat()
                is_dir = e.is_dir(follow_symlinks=False)
                ext = (
                    os.path.splitext(e.name)[1].lower().lstrip(".")
                    if not is_dir
                    else ""
                )
                hidden = False
                if sys.platform == "win32":
                    try:
                        hidden = bool(st.st_file_attributes & 2)
                    except Exception:
                        pass
                else:
                    hidden = e.name.startswith(".")
                items.append({
                    "name": e.name,
                    "path": e.path.replace("\\", "/"),
                    "type": "folder" if is_dir else (ext or "file"),
                    "size": "" if is_dir else fmt_size(st.st_size),
                    "size_b": 0 if is_dir else st.st_size,
                    "date": fmt_date(st.st_mtime),
                    "date_ts": st.st_mtime,
                    "hidden": hidden,
                })
            except Exception:
                pass
    except Exception:
        pass
    return items


def get_specials():
    home = os.path.expanduser("~")
    m = {
        "desktop": os.path.join(home, "Desktop"),
        "documents": os.path.join(home, "Documents"),
        "downloads": os.path.join(home, "Downloads"),
        "pictures": os.path.join(home, "Pictures"),
        "music": os.path.join(home, "Music"),
        "videos": os.path.join(home, "Videos"),
        "home": home,
    }
    return {k: v.replace("\\", "/") for k, v in m.items() if os.path.isdir(v)}


def open_path(target):
    os.startfile(target)


def reveal_in_explorer(target):
    if os.path.exists(target):
        subprocess.Popen(["explorer", "/select,", os.path.normpath(target)])
    else:
        subprocess.Popen(["explorer", os.path.normpath(target)])


def mkdir(path):
    os.makedirs(path, exist_ok=True)


def rename(src, dst):
    os.rename(src, dst)


def delete_to_recycle(paths):
    errors = []
    for t in paths:
        try:
            if sys.platform == "win32":
                t_esc = t.replace("'", "''")
                subprocess.run(
                    [
                        "powershell", "-NoProfile", "-Command",
                        "Add-Type -AssemblyName Microsoft.VisualBasic; "
                        f"[Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile("
                        f"'{t_esc}','OnlyErrorDialogs','SendToRecycleBin')",
                    ],
                    capture_output=True,
                    timeout=15,
                )
            else:
                if os.path.isdir(t):
                    shutil.rmtree(t)
                else:
                    os.remove(t)
        except Exception as e:
            errors.append(str(e))
    return errors


def copy_items(items):
    errors = []
    for item in items:
        try:
            src, dst = item["src"], item["dst"]
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        except Exception as e:
            errors.append(str(e))
    return errors


def move_items(items):
    errors = []
    for item in items:
        try:
            shutil.move(item["src"], item["dst"])
        except Exception as e:
            errors.append(str(e))
    return errors


def powertoys_preview(path):
    if sys.platform != "win32":
        os.startfile(path)
        return

    path = os.path.normpath(path)
    pf = os.environ.get("ProgramFiles", "C:\\Program Files")
    pf86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
    lapp = os.environ.get("LOCALAPPDATA", "")

    candidates = []
    for base in (pf, pf86, lapp):
        candidates += [
            os.path.join(base, "PowerToys", "WinUI3Apps", "PowerToys.Peek.UI.exe"),
            os.path.join(base, "PowerToys", "FilePreviewHost.exe"),
        ]

    peek_exe = None
    for c in candidates:
        if os.path.isfile(c):
            peek_exe = c
            break

    if peek_exe and "Peek" in peek_exe:
        try:
            subprocess.Popen([peek_exe, path])
            return
        except Exception:
            pass

    try:
        uri = "ms-peek://preview?FilePath=" + urllib.parse.quote(path, safe="")
        os.startfile(uri)
        return
    except Exception:
        pass

    try:
        subprocess.Popen(["explorer", "/select,", path])
        return
    except Exception:
        pass

    try:
        os.startfile(path)
    except Exception:
        pass
