# -*- coding: utf-8 -*-
"""Accès rapide Windows — lecture via Shell COM (même source que l'Explorateur)."""
import json
import os
import subprocess
import sys
import threading

QA_NAMESPACE = "shell:::{679F85CB-0220-4080-B29B-5540CC05AAB6}"

_PS_LIST = r"""
$ErrorActionPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$shell = New-Object -ComObject Shell.Application
$qa = $shell.Namespace('{ns}')
$out = @()
foreach ($item in $qa.Items()) {{
    $p = $item.Path
    if (-not $p) {{ continue }}
    $out += [ordered]@{{
        name = [string]$item.Name
        path = [string]$p
    }}
}}
$out | ConvertTo-Json -Compress -Depth 3
""".format(ns=QA_NAMESPACE)


def _qa_dest_watch_paths():
    """Fichiers susceptibles de changer quand l'Accès rapide est modifié."""
    paths = []
    appdata = os.environ.get("APPDATA", "")
    auto_dir = os.path.join(appdata, "Microsoft", "Windows", "Recent", "AutomaticDestinations")
    if os.path.isdir(auto_dir):
        paths.append(auto_dir)
        for name in os.listdir(auto_dir):
            low = name.lower()
            if "f01b4" in low and low.endswith(".automaticdestinations-ms"):
                paths.append(os.path.join(auto_dir, name))
    custom = os.path.join(
        os.environ.get("LOCALAPPDATA", ""),
        "Microsoft", "Windows", "Explorer",
    )
    if os.path.isdir(custom):
        paths.append(custom)
    return paths


def _snapshot(paths):
  sig = []
  for p in paths:
    try:
      if os.path.isfile(p):
        sig.append((p, os.path.getmtime(p), os.path.getsize(p)))
      elif os.path.isdir(p):
        sig.append((p, os.path.getmtime(p), len(os.listdir(p))))
    except OSError:
      sig.append((p, 0, 0))
  return tuple(sig)


def get_quick_access_items():
    """
    Retourne les entrées de l'Accès rapide (épinglés + emplacements par défaut),
    dans le même ordre que l'Explorateur Windows.
    """
    if sys.platform != "win32":
        return []
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", _PS_LIST],
            capture_output=True,
            timeout=20,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        raw = (r.stdout or b"").decode("utf-8", errors="replace").strip()
        if not raw or r.returncode != 0:
            return []
        data = json.loads(raw)
        if isinstance(data, dict):
            data = [data]
        items = []
        seen = set()
        for row in data:
            path = (row.get("path") or "").strip()
            name = (row.get("name") or os.path.basename(path) or path).strip()
            if not path:
                continue
            norm = path.replace("\\", "/")
            key = norm.lower()
            if key in seen:
                continue
            seen.add(key)
            if os.path.isdir(path) or norm.startswith("//"):
                items.append({"name": name, "path": norm})
        return items
    except Exception:
        return []


class QuickAccessWatcher:
    """Surveille les fichiers Shell liés à l'Accès rapide et notifie les changements."""

    def __init__(self, on_change, interval=5.0):
        self._on_change = on_change
        self._interval = interval
        self._stop = threading.Event()
        self._thread = None
        self._items_sig = None
        self._fs_sig = None
        self._watch_paths = _qa_dest_watch_paths()

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def refresh_now(self):
        """Force une lecture immédiate (ex. au focus de la fenêtre)."""
        threading.Thread(target=self._poll, daemon=True).start()

    def _items_signature(self, items):
        return tuple((i["path"], i["name"]) for i in items)

    def _poll(self):
        items = get_quick_access_items()
        fs_sig = _snapshot(self._watch_paths)
        items_sig = self._items_signature(items)
        if items_sig != self._items_sig or fs_sig != self._fs_sig:
            self._items_sig = items_sig
            self._fs_sig = fs_sig
            self._on_change(items)

    def _loop(self):
        self._poll()
        while not self._stop.wait(self._interval):
            self._poll()
