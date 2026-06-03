# -*- coding: utf-8 -*-
"""FINDexplorER — Interface CustomTkinter style Windows 11."""
import os
import sys
import re
import time
import threading
import tkinter as tk
import customtkinter as ctk
import fe_backend as be
import fe_quickaccess as qa

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

FONT    = "Segoe UI"
FONT_SM = (FONT, 11)
FONT_MD = (FONT, 12)
FONT_LG = (FONT, 13, "bold")
FONT_TITLE = (FONT, 13, "bold")

SIDEBAR_W = 188
ROW_H     = 28
ICON_CELL = 88

_ACCENT_CACHE = None
_ICON_CACHE   = {}

def _accent():
    global _ACCENT_CACHE
    if _ACCENT_CACHE is not None:
        return _ACCENT_CACHE
    c = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
    _ACCENT_CACHE = c[0] if isinstance(c, (tuple, list)) else c
    return _ACCENT_CACHE

def _cached_icon(it):
    key = (it.get("type"), (it.get("name") or "").split(".")[-1].lower())
    if key not in _ICON_CACHE:
        _ICON_CACHE[key] = be.item_icon(it)
    return _ICON_CACHE[key]

def _ico_path():
    here = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    p = os.path.join(here, "FindExplorer.ico")
    if not os.path.isfile(p):
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "FindExplorer.ico")
    return p


class ExplorerApp(ctk.CTk):
    """Explorateur fichiers FINDexplorER."""

    # ── Init ──────────────────────────────────────────────────────────────────

    def __init__(self):
        super().__init__()
        self.attributes("-alpha", 0)
        self.geometry("960x640+-9999+-9999")
        self.withdraw()
        self.title("FINDexplorER")
        self.minsize(720, 480)
        ico = _ico_path()
        if os.path.isfile(ico):
            try:
                self.iconbitmap(ico)
            except Exception:
                pass

        self._visible       = False
        self.items          = []
        self.sel            = set()
        self.hist           = []
        self.hist_idx       = -1
        self.view_mode      = "list"
        self.sort_key       = "name"
        self.sort_asc       = True
        self.show_hid       = False
        self.clipboard      = None
        self.specials       = {}
        self.last_idx       = -1
        self.focus_panel    = "files"
        self.side_idx       = 0
        self.search_buf     = ""
        self._search_after  = None
        self._loading       = False
        self._row_widgets   = []
        self._display_list  = []
        self._side_buttons  = []
        self._qa_items      = []
        self._qa_watcher    = None
        self._last_ctrl_tab = 0.0
        self._sel_colors    = None
        self._last_pathbar  = None   # cache pathbar pour éviter rebuild inutile

        self._build_chrome()
        self._bind_keys()
        self.bind("<FocusIn>", lambda _e: self._on_app_focus())
        self.protocol("WM_DELETE_WINDOW", self.hide_app)
        self.after(50, self._startup)

    # ── Construction UI ───────────────────────────────────────────────────────

    def _build_chrome(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._path_frame = ctk.CTkFrame(self, height=40, corner_radius=0,
                                        fg_color="transparent")
        self._path_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
        self._path_inner = ctk.CTkFrame(self._path_frame, fg_color="transparent")
        self._path_inner.pack(fill="x")

        self._main = ctk.CTkFrame(self, corner_radius=12, border_width=1)
        self._main.grid(row=1, column=0, sticky="nsew", padx=12, pady=4)
        self._main.grid_columnconfigure(1, weight=1)
        self._main.grid_rowconfigure(0, weight=1)

        self._sidebar = ctk.CTkScrollableFrame(
            self._main, width=SIDEBAR_W, corner_radius=10,
            label_text="", fg_color=("gray92", "gray17"),
        )
        self._sidebar.grid(row=0, column=0, sticky="ns", padx=(8, 4), pady=8)

        self._filezone = ctk.CTkFrame(self._main, corner_radius=10,
                                      fg_color="transparent")
        self._filezone.grid(row=0, column=1, sticky="nsew", padx=(4, 8), pady=8)
        self._filezone.grid_columnconfigure(0, weight=1)
        self._filezone.grid_rowconfigure(1, weight=1)

        hdr = ctk.CTkFrame(self._filezone, height=32, corner_radius=8,
                           fg_color=("gray90", "gray20"))
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        hdr.grid_columnconfigure(0, weight=3)
        hdr.grid_columnconfigure(1, weight=1)
        hdr.grid_columnconfigure(2, weight=1)
        hdr.grid_columnconfigure(3, weight=0)
        self._hdr_name = ctk.CTkButton(
            hdr, text="Nom ▼", font=FONT_SM, height=28, corner_radius=6,
            fg_color="transparent", hover_color=("gray85", "gray25"),
            command=lambda: self._set_sort("name"))
        self._hdr_name.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        self._hdr_size = ctk.CTkButton(
            hdr, text="Taille", font=FONT_SM, height=28, corner_radius=6,
            fg_color="transparent", hover_color=("gray85", "gray25"),
            command=lambda: self._set_sort("size"))
        self._hdr_size.grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        self._hdr_date = ctk.CTkButton(
            hdr, text="Modifié", font=FONT_SM, height=28, corner_radius=6,
            fg_color="transparent", hover_color=("gray85", "gray25"),
            command=lambda: self._set_sort("date"))
        self._hdr_date.grid(row=0, column=2, sticky="ew", padx=2, pady=2)
        self._about_btn = ctk.CTkButton(
            hdr, text="ℹ", width=32, height=28, corner_radius=6,
            font=(FONT, 10), fg_color="transparent",
            hover_color=("gray85", "gray25"), command=self._show_about)
        self._about_btn.grid(row=0, column=3, sticky="e", padx=2, pady=2)
        self._list_hdr = hdr

        self._files_scroll = ctk.CTkScrollableFrame(
            self._filezone, corner_radius=8, fg_color=("gray96", "gray14"))
        self._files_scroll.grid(row=1, column=0, sticky="nsew")
        self._files_scroll.grid_columnconfigure(0, weight=1)

        # ── Barre de statut ──
        self._status = ctk.CTkFrame(self, height=28, corner_radius=0,
                                    fg_color="transparent")
        self._status.grid(row=2, column=0, sticky="ew", padx=14, pady=(4, 10))
        self._st_count = ctk.CTkLabel(self._status, text="—", font=FONT_SM,
                                      text_color=("gray40", "gray60"))
        self._st_count.pack(side="left")
        self._st_sel = ctk.CTkLabel(self._status, text="", font=FONT_SM,
                                    text_color=("gray40", "gray60"))
        self._st_sel.pack(side="left", padx=(14, 0))
        self._st_search = ctk.CTkLabel(self._status, text="", font=FONT_SM,
                                       text_color=_accent())
        self._st_search.pack(side="left", padx=(14, 0))
        self._st_clip = ctk.CTkLabel(self._status, text="", font=FONT_SM,
                                     text_color=("gray40", "gray60"))
        self._st_clip.pack(side="right")

        self._loading_frame = ctk.CTkFrame(self, corner_radius=12,
                                           fg_color=("gray90", "gray18"))
        self._loading_lbl = ctk.CTkLabel(self._loading_frame,
                                         text="Chargement…", font=FONT_MD)
        self._loading_lbl.pack(padx=40, pady=30)
        self._loading_frame.place_forget()

        self._toast = ctk.CTkLabel(
            self, text="", font=FONT_SM, corner_radius=8,
            fg_color=("gray20", "gray88"), text_color=("white", "gray10"))

    # ── Bindings clavier ──────────────────────────────────────────────────────

    def _bind_keys(self):
        self.bind_all("<Key>", self._on_key, add="+")
        for seq in ("<Control-Tab>", "<Control-ISO_Left_Tab>"):
            self.bind(seq, self._on_ctrl_tab_event)
            self.bind_all(seq, self._on_ctrl_tab_event)
        self._neutralize_ctrl_tab_native()

    def _neutralize_ctrl_tab_native(self):
        """Supprime le focus-traversal natif de Tkinter pour Ctrl+Tab."""
        for seq in ("<Control-Tab>", "<Control-ISO_Left_Tab>"):
            for cls in ("TNotebook", "TFrame", "TScrollableFrame", "Toplevel",
                        "Frame", "Canvas", "CTkFrame", "CTkScrollableFrame",
                        "CTkButton", "CTkLabel", "CTkEntry"):
                try:
                    self.unbind_class(cls, seq)
                except Exception:
                    pass

    # ── Visibilité ────────────────────────────────────────────────────────────

    def toggle_visibility(self):
        if self._visible:
            self.withdraw()
            self._visible = False
        else:
            x, y = self.winfo_x(), self.winfo_y()
            if x < -100 or y < -100:
                sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
                w, h = 960, 640
                self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
            self.deiconify()
            self.attributes("-alpha", 1)
            self.lift()
            self.focus_force()
            self._visible = True

    def hide_app(self):
        self.toggle_visibility()

    # ── Toast / chargement ────────────────────────────────────────────────────

    def toast(self, msg):
        self._toast.configure(text=msg)
        self._toast.place(relx=0.5, rely=0.92, anchor="center")
        self.after(2200, lambda: self._toast.place_forget())

    def _show_loading(self, on):
        self._loading = bool(on)
        if on:
            self._loading_frame.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self._loading_frame.place_forget()

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        for w in self._sidebar.winfo_children():
            w.destroy()
        self._side_buttons = []

        def sect(title):
            ctk.CTkLabel(self._sidebar, text=title, font=(FONT, 10),
                         text_color=("gray50", "gray55"),
                         ).pack(anchor="w", padx=8, pady=(10, 2))

        def entry(label, icon, cmd, path=None):
            btn = ctk.CTkButton(
                self._sidebar, text=f"  {icon}  {label}", anchor="w",
                font=FONT_SM, height=30, corner_radius=8,
                fg_color="transparent", hover_color=("gray88", "gray28"),
                command=cmd)
            btn.pack(fill="x", padx=6, pady=1)
            btn._fe_path = path
            self._side_buttons.append(btn)
            return btn

        sect("Accès rapide")
        if not self._qa_items:
            ctk.CTkLabel(self._sidebar, text="  Chargement…", font=FONT_SM,
                         text_color=("gray50", "gray55"),
                         ).pack(anchor="w", padx=10, pady=4)
        else:
            for it in self._qa_items:
                p = it["path"]
                label = it["name"][:22] + "…" if len(it["name"]) > 24 else it["name"]
                entry(label, "📌", lambda path=p: self._sidebar_go(path), path=p)

        sect("Appareils")
        for drv in be.get_drives():
            p = drv["path"]
            entry(drv["name"], "💾", lambda path=p: self._sidebar_go(path), path=p)

        # Neutraliser après chaque rebuild car les nouveaux widgets CTk
        # réinstallent les bindings natifs Ctrl+Tab sur leurs classes
        self._neutralize_ctrl_tab_native()

    def _apply_quick_access(self, items):
        self._qa_items = items
        self._build_sidebar()
        self._update_sidebar_active()

    def _start_quick_access_watch(self):
        def on_change(items):
            self.after(0, lambda: self._apply_quick_access(items))
        self._qa_watcher = qa.QuickAccessWatcher(on_change, interval=5.0)
        self._qa_watcher.start()

    def _on_app_focus(self):
        if self._qa_watcher:
            self._qa_watcher.refresh_now()

    # ── Navigation ────────────────────────────────────────────────────────────

    def _startup(self):
        self.specials  = be.get_specials()
        self._qa_items = qa.get_quick_access_items()
        self._build_sidebar()
        self._start_quick_access_watch()
        start = self.specials.get("desktop") or next(iter(self.specials.values()), None) or "C:/"
        if self._qa_items:
            start = self._qa_items[0]["path"]
        self._nav_to(start, no_history=True)

    def _sidebar_go(self, path):
        self.focus_panel = "files"
        self._nav_to(path)

    def _nav_to(self, path, no_history=False):
        path = be.normalize_path(path)
        if not no_history:
            self.hist = self.hist[: self.hist_idx + 1]
            self.hist.append(path)
            self.hist_idx += 1
        else:
            if self.hist_idx < 0:
                self.hist     = [path]
                self.hist_idx = 0
            else:
                self.hist[self.hist_idx] = path
        self.cur_path = path
        self.sel.clear()
        self.last_idx = -1
        self._reset_search()
        self._load_dir()

    def _load_dir(self):
        def work():
            self.after(0, lambda: self._show_loading(True))
            try:
                items = be.list_dir(self.cur_path)
            except Exception:
                items = []
            self.after(0, lambda: self._on_dir_loaded(items))
        threading.Thread(target=work, daemon=True).start()

    def _on_dir_loaded(self, items):
        self.items = items
        self._show_loading(False)
        self._render()
        if not self._visible:
            self.update_idletasks()
            sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
            w, h = 960, 640
            self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
            self.deiconify()
            self.attributes("-alpha", 1)
            self.lift()
            self.focus_force()
            self._visible = True

    def _nav_drives(self):
        self.cur_path = ""
        self.sel.clear()
        self.last_idx = -1
        self._reset_search()
        self.hist = self.hist[: self.hist_idx + 1]
        self.hist.append("")
        self.hist_idx += 1
        self.items = be.get_drives()
        self._render()

    def _nav_special(self, key):
        p = self.specials.get(key)
        if p:
            self._nav_to(p)

    def _go_back(self):
        if self.hist_idx > 0:
            self.hist_idx -= 1
            self.cur_path  = self.hist[self.hist_idx]
            self.sel.clear()
            self._load_dir()

    def _go_fwd(self):
        if self.hist_idx < len(self.hist) - 1:
            self.hist_idx += 1
            self.cur_path  = self.hist[self.hist_idx]
            self.sel.clear()
            self._load_dir()

    def _go_up(self):
        if not self.cur_path:
            return
        parts = [p for p in self.cur_path.replace("\\", "/").split("/") if p]
        if len(parts) <= 1:
            if parts and re.match(r"^[A-Za-z]:$", parts[0]):
                self._nav_drives()
            return
        parts.pop()
        base = parts[0] if parts else ""
        if len(parts) == 1 and re.match(r"^[A-Za-z]:$", base):
            self._nav_to(base + "/")
        else:
            self._nav_to("/".join(parts))

    # ── Tri ───────────────────────────────────────────────────────────────────

    def _sorted_items(self):
        lst = [it for it in self.items if self.show_hid or not it.get("hidden")]
        sk  = self.sort_key
        rev = not self.sort_asc

        def key(it):
            if sk == "size":  return it.get("size_b") or 0
            if sk == "date":  return it.get("date_ts") or 0
            if sk == "type":  return it.get("type") or ""
            return (it.get("name") or "").lower()

        folders = sorted([x for x in lst if x.get("type") in ("folder", "drive")],
                         key=key, reverse=rev)
        files   = sorted([x for x in lst if x.get("type") not in ("folder", "drive")],
                         key=key, reverse=rev)
        return folders + files

    def _set_sort(self, k):
        if self.sort_key == k:
            self.sort_asc = not self.sort_asc
        else:
            self.sort_key = k
            self.sort_asc = True
        self._render()

    def _set_view(self, mode):
        self.view_mode = mode
        self._render()

    # ── Rendu ─────────────────────────────────────────────────────────────────

    def _render_pathbar(self):
        path = self.cur_path or ""
        if path == self._last_pathbar:
            return   # pas de changement : éviter de reconstruire pour rien
        self._last_pathbar = path

        for w in self._path_inner.winfo_children():
            w.destroy()

        if not path:
            ctk.CTkButton(self._path_inner, text="Poste de travail", font=FONT_SM,
                          height=28, corner_radius=8, fg_color="transparent",
                          hover_color=("gray88", "gray28"),
                          command=self._nav_drives).pack(side="left")
            return

        parts = [p for p in path.replace("\\", "/").split("/") if p]
        root  = (parts[0] if parts else "C:").split(":")[0] + ":"
        acc   = root + "/"

        def seg(text, p):
            ctk.CTkButton(self._path_inner, text=text, font=FONT_SM, height=28,
                          corner_radius=8, fg_color="transparent",
                          hover_color=("gray88", "gray28"),
                          command=lambda _p=p: self._nav_to(_p)).pack(side="left")

        seg(root, acc)
        for s in parts[1:]:
            ctk.CTkLabel(self._path_inner, text=" › ", font=FONT_SM,
                         text_color=("gray55", "gray50")).pack(side="left")
            acc = acc.rstrip("/") + "/" + s
            seg(s, acc)

    def _path_under(self, base):
        if not base or not self.cur_path:
            return False
        cur  = be.normalize_path(self.cur_path)
        base = be.normalize_path(base)
        return cur == base or cur.startswith(base + "/")

    def _update_sidebar_active(self):
        accent = _accent()
        loc_fg = ("gray86", "gray28")
        norm_txt = ctk.ThemeManager.theme["CTkButton"]["text_color"]
        for i, btn in enumerate(self._side_buttons):
            p          = getattr(btn, "_fe_path", None)
            is_loc     = bool(p and self.cur_path and self._path_under(p))
            is_kb      = self.focus_panel == "sidebar" and i == self.side_idx
            if is_kb:
                btn.configure(fg_color=accent, text_color=("white", "white"),
                              border_width=0)
            elif is_loc:
                btn.configure(fg_color=loc_fg, text_color=norm_txt, border_width=0)
            else:
                btn.configure(fg_color="transparent", text_color=norm_txt,
                              border_width=0)

    def _update_status(self):
        lst     = self._display_list
        folders = sum(1 for i in lst if i.get("type") == "folder")
        files   = len(lst) - folders
        txt = f"{len(lst)} élément{'s' if len(lst) != 1 else ''}"
        if folders: txt += f" · {folders} dossier{'s' if folders != 1 else ''}"
        if files:   txt += f" · {files} fichier{'s' if files != 1 else ''}"
        self._st_count.configure(text=txt)
        self._st_sel.configure(
            text=f"{len(self.sel)} sélectionné{'s' if len(self.sel) != 1 else ''}"
            if self.sel else "")
        if self.clipboard:
            n    = len(self.clipboard.get("items", []))
            mode = self.clipboard.get("mode")
            self._st_clip.configure(
                text=f"✂ {n} à couper" if mode == "cut" else f"📋 {n} copiés")
        else:
            self._st_clip.configure(text="")

    def _update_sort_headers(self):
        for k, btn, base in (
            ("name", self._hdr_name, "Nom"),
            ("size", self._hdr_size, "Taille"),
            ("date", self._hdr_date, "Modifié"),
        ):
            arr = (" ▼" if self.sort_asc else " ▲") if self.sort_key == k else ""
            btn.configure(text=base + arr)

    def _render(self):
        self._display_list = self._sorted_items()
        self._sel_colors   = None
        self._render_pathbar()
        self._update_sidebar_active()
        self._update_status()
        self._update_sort_headers()
        if self.view_mode == "icons":
            self._list_hdr.grid_remove()
            self._render_icons()
        else:
            self._list_hdr.grid()
            self._render_list()

    def _cut_paths(self):
        if self.clipboard and self.clipboard.get("mode") == "cut":
            return {x["path"] for x in self.clipboard.get("items", [])}
        return set()

    def _clear_files(self):
        for w in self._files_scroll.winfo_children():
            w.destroy()
        self._row_widgets = []

    # ── Rendu liste ───────────────────────────────────────────────────────────

    def _render_list(self):
        lst = self._display_list
        self._clear_files()
        if not lst:
            ctk.CTkLabel(self._files_scroll, text="📂  Dossier vide",
                         font=FONT_MD, text_color=("gray50", "gray55"),
                         ).pack(pady=40)
            return

        cut_paths = self._cut_paths()
        for i, it in enumerate(lst):
            row = ctk.CTkFrame(self._files_scroll, height=ROW_H, corner_radius=6,
                               fg_color="transparent")
            row.pack(fill="x", padx=4, pady=1)
            row.grid_columnconfigure(0, weight=3)
            row.grid_columnconfigure(1, weight=1)
            row.grid_columnconfigure(2, weight=1)

            name_lbl = ctk.CTkLabel(row, text=f"{_cached_icon(it)}  {it['name']}",
                                    anchor="w", font=FONT_SM)
            name_lbl.grid(row=0, column=0, sticky="ew", padx=8)
            size_lbl = ctk.CTkLabel(row, text=it.get("size") or "—",
                                    anchor="e", font=FONT_SM)
            size_lbl.grid(row=0, column=1, sticky="ew", padx=4)
            date_lbl = ctk.CTkLabel(row, text=it.get("date") or "—",
                                    anchor="w", font=FONT_SM)
            date_lbl.grid(row=0, column=2, sticky="ew", padx=8)

            row._fe_idx    = i
            row._fe_labels = (name_lbl, size_lbl, date_lbl)
            self._row_widgets.append(row)
            self._sel_style(row, i in self.sel, it["path"] in cut_paths)

            for w in (row, name_lbl, size_lbl, date_lbl):
                w.bind("<Button-1>",        lambda e, idx=i: self._click_item(e, idx))
                w.bind("<Double-Button-1>", lambda e, idx=i: self._dbl_item(idx))

    def _update_sel_visual(self, indices=None):
        cut = self._cut_paths()
        idx_map = {getattr(r, "_fe_idx", -1): r for r in self._row_widgets}
        targets = (
            [idx_map[i] for i in indices if i in idx_map]
            if indices is not None else self._row_widgets
        )
        for row in targets:
            i = getattr(row, "_fe_idx", -1)
            if 0 <= i < len(self._display_list):
                self._sel_style(row, i in self.sel,
                                self._display_list[i]["path"] in cut)
        self._st_sel.configure(
            text=(f"{len(self.sel)} sélectionné{'s' if len(self.sel) != 1 else ''}"
                  if self.sel else ""))

    def _sel_style(self, frame, selected, cut=False):
        if self._sel_colors is None:
            self._sel_colors = {
                "sel_fg":   _accent(),
                "cut_fg":   ("gray94", "gray22"),
                "norm_fg":  "transparent",
                "sel_txt":  ("white", "white"),
                "cut_txt":  ("gray55", "gray50"),
                "norm_txt": ctk.ThemeManager.theme["CTkLabel"]["text_color"],
            }
        c = self._sel_colors
        if selected:
            frame.configure(fg_color=c["sel_fg"])
            fg = c["sel_txt"]
        elif cut:
            frame.configure(fg_color=c["cut_fg"])
            fg = c["cut_txt"]
        else:
            frame.configure(fg_color=c["norm_fg"])
            fg = c["norm_txt"]
        labels = getattr(frame, "_fe_labels", None)
        if labels:
            for lbl in labels:
                lbl.configure(text_color=fg)
        else:
            for ch in frame.winfo_children():
                if isinstance(ch, ctk.CTkLabel):
                    ch.configure(text_color=fg)

    def _render_icons(self):
        self._clear_files()
        lst       = self._display_list
        cut_paths = self._cut_paths()
        if not lst:
            ctk.CTkLabel(self._files_scroll, text="📂  Dossier vide",
                         font=FONT_MD, text_color=("gray50", "gray55"),
                         ).pack(pady=40)
            return
        grid = ctk.CTkFrame(self._files_scroll, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=4, pady=4)
        cols = max(4, (self.winfo_width() or 800) // ICON_CELL)
        for i, it in enumerate(lst):
            cell = ctk.CTkFrame(grid, width=ICON_CELL - 8, height=ICON_CELL,
                                corner_radius=10, fg_color="transparent")
            r, c = divmod(i, cols)
            cell.grid(row=r, column=c, padx=4, pady=4)
            ctk.CTkLabel(cell, text=be.item_icon(it), font=(FONT, 26)).pack(pady=(6, 2))
            ctk.CTkLabel(cell, text=it["name"], font=(FONT, 10),
                         wraplength=ICON_CELL - 16).pack(padx=4)
            cell._fe_idx = i
            self._row_widgets.append(cell)
            self._sel_style(cell, i in self.sel, it["path"] in cut_paths)
            cell.bind("<Button-1>",        lambda e, idx=i: self._click_item(e, idx))
            cell.bind("<Double-Button-1>", lambda e, idx=i: self._dbl_item(idx))

    # ── Sélection / scroll ────────────────────────────────────────────────────

    def _click_item(self, ev, idx):
        prev = set(self.sel)
        if ev.state & 0x4:
            self.sel.discard(idx) if idx in self.sel else self.sel.add(idx)
        elif ev.state & 0x1 and self.last_idx >= 0:
            lo, hi = min(idx, self.last_idx), max(idx, self.last_idx)
            if not (ev.state & 0x4):
                self.sel.clear()
            self.sel.update(range(lo, hi + 1))
        else:
            self.sel.clear()
            self.sel.add(idx)
        self.last_idx = idx
        self._update_sel_visual(prev | self.sel)

    def _dbl_item(self, idx):
        lst = self._display_list
        if not lst or idx >= len(lst):
            return
        it = lst[idx]
        if it.get("type") in ("folder", "drive"):
            self._nav_to(it["path"])
        else:
            try:
                be.open_path(it["path"])
            except Exception:
                self.toast("Impossible d'ouvrir")

    def _scroll_to_idx(self, idx):
        """Défile le minimum nécessaire pour rendre la ligne idx visible."""
        # after(0) laisse Tkinter terminer le pack/grid avant de lire les coordonnées
        self.after(0, lambda: self._do_scroll_to_idx(idx))

    def _do_scroll_to_idx(self, idx):
        if idx < 0 or idx >= len(self._display_list):
            return
        # Trouver le widget correspondant à idx dans _row_widgets
        # (on cherche par _fe_idx, pas par position, car le vide peut décaler)
        w = None
        for rw in self._row_widgets:
            if getattr(rw, "_fe_idx", -1) == idx:
                w = rw
                break
        if w is None:
            return
        try:
            canvas = self._files_scroll._parent_canvas
            # Coordonnées écran absolues
            row_top    = w.winfo_rooty()
            row_bot    = row_top + w.winfo_height()
            canvas_top = canvas.winfo_rooty()
            canvas_bot = canvas_top + canvas.winfo_height()

            if row_top >= canvas_top and row_bot <= canvas_bot:
                return   # déjà entièrement visible

            # Région scrollable totale
            view_frac = canvas.yview()
            frac_size = view_frac[1] - view_frac[0]
            if frac_size <= 0:
                return
            total_h = canvas.winfo_height() / frac_size

            if row_top < canvas_top:
                delta = row_top - canvas_top          # remonter
            else:
                delta = row_bot - canvas_bot          # descendre

            new_frac = view_frac[0] + delta / total_h
            canvas.yview_moveto(max(0.0, min(1.0, new_frac)))
        except Exception:
            pass

    # ── Sélection utilitaires ─────────────────────────────────────────────────

    def _get_sel_items(self):
        lst = self._display_list
        return [lst[i] for i in sorted(self.sel) if i < len(lst)]

    def _select_all(self):
        self.sel = set(range(len(self._display_list)))
        self._update_sel_visual()

    def _invert_sel(self):
        all_idx = set(range(len(self._display_list)))
        self.sel = all_idx - self.sel
        self._update_sel_visual()

    def _open_sel(self):
        if len(self.sel) == 1:
            self._dbl_item(next(iter(self.sel)))

    def _reveal(self):
        items  = self._get_sel_items()
        target = items[0]["path"] if items else self.cur_path
        try:
            be.reveal_in_explorer(target)
        except Exception:
            self.toast("Erreur")

    # ── Actions fichiers ──────────────────────────────────────────────────────

    def _new_folder(self):
        self._input_dialog("Nouveau dossier", "Nom du dossier :",
                           "Dossier sans titre", self._do_mkdir)

    def _do_mkdir(self, name):
        if not name.strip():
            return
        path = self.cur_path.rstrip("/") + "/" + name.strip()
        try:
            be.mkdir(path)
            self.toast("Dossier créé")
            self._load_dir()
        except Exception as e:
            self.toast(f"Erreur : {e}")

    def _rename_sel(self):
        items = self._get_sel_items()
        if len(items) != 1:
            self.toast("Sélectionnez un seul élément")
            return
        it = items[0]
        self._input_dialog("Renommer", "Nouveau nom :", it["name"],
                           lambda n: self._do_rename(it, n))

    def _do_rename(self, it, name):
        if not name.strip() or name == it["name"]:
            return
        d = "/".join(it["path"].replace("\\", "/").split("/")[:-1])
        try:
            be.rename(it["path"], d + "/" + name.strip())
            self.toast("Renommé")
            self.sel.clear()
            self._load_dir()
        except Exception as e:
            self.toast(f"Erreur : {e}")

    def _delete_sel(self):
        items = self._get_sel_items()
        if not items:
            return
        msg = (f'Mettre "{items[0]["name"]}" à la corbeille ?'
               if len(items) == 1
               else f"Mettre {len(items)} éléments à la corbeille ?")
        self._confirm_dialog(msg, lambda: self._do_delete(items))

    def _do_delete(self, items):
        errs = be.delete_to_recycle([i["path"] for i in items])
        self.toast("Erreur suppression" if errs
                   else "Supprimé" + ("s" if len(items) > 1 else ""))
        self.sel.clear()
        self._load_dir()

    def _cut_sel(self):
        items = self._get_sel_items()
        if not items:
            return
        self.clipboard = {"mode": "cut",
                          "items": [{"name": i["name"], "path": i["path"]}
                                    for i in items]}
        self._update_sel_visual()
        self._st_clip.configure(text=f"✂ {len(items)} à couper")

    def _copy_sel(self):
        items = self._get_sel_items()
        if not items:
            return
        self.clipboard = {"mode": "copy",
                          "items": [{"name": i["name"], "path": i["path"]}
                                    for i in items]}
        self._st_clip.configure(text=f"📋 {len(items)} copiés")

    def _paste(self):
        if not self.clipboard:
            return
        base = self.cur_path.rstrip("/")
        ops  = [{"src": it["path"], "dst": base + "/" + it["name"]}
                for it in self.clipboard["items"]]
        fn   = be.copy_items if self.clipboard["mode"] == "copy" else be.move_items
        errs = fn(ops)
        if errs:
            self.toast("Erreur : " + ", ".join(errs[:2]))
        else:
            self.toast("Copié" if self.clipboard["mode"] == "copy" else "Déplacé")
            if self.clipboard["mode"] == "cut":
                self.clipboard = None
        self.sel.clear()
        self._load_dir()

    def _duplicate_sel(self):
        items = self._get_sel_items()
        if not items:
            return
        base = self.cur_path.rstrip("/")
        errs = be.copy_items(
            [{"src": it["path"], "dst": base + "/Copie de " + it["name"]}
             for it in items])
        self.toast("Erreur" if errs else "Dupliqué")
        if not errs:
            self._load_dir()

    def _preview_file(self, path):
        try:
            be.powertoys_preview(path)
        except Exception:
            self.toast("Prévisualisation indisponible")

    # ── Recherche incrémentale ────────────────────────────────────────────────

    def _reset_search(self):
        self.search_buf = ""
        self._st_search.configure(text="")
        if self._search_after:
            self.after_cancel(self._search_after)
            self._search_after = None

    def _do_search(self, char):
        if self._search_after:
            self.after_cancel(self._search_after)
        self.search_buf += char.lower()
        lst = self._display_list   # utilise la liste déjà triée, pas _sorted_items()
        nx = next((i for i, it in enumerate(lst)
                   if it["name"].lower().startswith(self.search_buf)), -1)
        if nx < 0:
            self.search_buf = char.lower()
            nx = next((i for i, it in enumerate(lst)
                       if it["name"].lower().startswith(self.search_buf)), -1)
        self._st_search.configure(
            text=f"🔍 {self.search_buf}" + ("" if nx >= 0 else " —"))
        if nx >= 0:
            prev = set(self.sel)
            self.sel = {nx}
            self.last_idx = nx
            self._update_sel_visual(prev | {nx})
            self._scroll_to_idx(nx)
        self._search_after = self.after(800, self._reset_search)

    # ── Dialogues ─────────────────────────────────────────────────────────────

    def _input_dialog(self, title, msg, default, on_ok):
        dlg = ctk.CTkToplevel(self)
        dlg.title(title)
        dlg.geometry("380x180")
        dlg.transient(self)
        dlg.grab_set()
        dlg.attributes("-topmost", True)
        ctk.CTkLabel(dlg, text=title, font=FONT_TITLE).pack(padx=20, pady=(16, 4))
        ctk.CTkLabel(dlg, text=msg, font=FONT_SM).pack(padx=20)
        entry = ctk.CTkEntry(dlg, width=320, font=FONT_MD, corner_radius=8)
        entry.pack(padx=20, pady=12)
        entry.insert(0, default)
        entry.focus_set()
        entry.select_range(0, "end")
        btns = ctk.CTkFrame(dlg, fg_color="transparent")
        btns.pack(pady=8)
        def ok():
            val = entry.get(); dlg.destroy(); on_ok(val)
        def cancel():
            dlg.destroy()
        ctk.CTkButton(btns, text="Annuler", width=100, corner_radius=8,
                      fg_color="transparent", border_width=1,
                      command=cancel).pack(side="left", padx=8)
        ctk.CTkButton(btns, text="OK", width=100, corner_radius=8,
                      command=ok).pack(side="left", padx=8)
        entry.bind("<Return>",  lambda e: ok())
        entry.bind("<Escape>",  lambda e: cancel())
        dlg.bind("<Escape>",    lambda e: cancel())

    def _confirm_dialog(self, msg, on_ok):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Confirmation")
        dlg.geometry("400x160")
        dlg.transient(self)
        dlg.grab_set()
        dlg.attributes("-topmost", True)
        ctk.CTkLabel(dlg, text=msg, font=FONT_MD,
                     wraplength=360).pack(padx=24, pady=24, expand=True)
        btns = ctk.CTkFrame(dlg, fg_color="transparent")
        btns.pack(pady=12)
        def ok():
            dlg.destroy(); on_ok()
        ctk.CTkButton(btns, text="Annuler", width=100, corner_radius=8,
                      fg_color="transparent", border_width=1,
                      command=dlg.destroy).pack(side="left", padx=8)
        ctk.CTkButton(btns, text="OK", width=100, corner_radius=8,
                      command=ok).pack(side="left", padx=8)
        dlg.bind("<Escape>", lambda e: dlg.destroy())

    # ── Focus panels ──────────────────────────────────────────────────────────

    def _on_ctrl_tab_event(self, event=None):
        if event and event.widget.winfo_class() in ("Entry", "CTkEntry"):
            return "break"
        now = time.time()
        if now - self._last_ctrl_tab < 0.12:
            return "break"
        self._last_ctrl_tab = now
        self._toggle_focus_panel()
        return "break"

    def _toggle_focus_panel(self):
        if self.focus_panel == "sidebar":
            self._focus_files()
        else:
            self._focus_sidebar()

    def _sidebar_open_selected(self):
        entries = self._side_buttons
        if not entries or self.side_idx >= len(entries):
            return
        path = getattr(entries[self.side_idx], "_fe_path", None)
        if path:
            self._sidebar_go(path)

    def _focus_sidebar(self):
        self.focus_panel = "sidebar"
        idx = 0
        for i, b in enumerate(self._side_buttons):
            p = getattr(b, "_fe_path", None)
            if p and self._path_under(p):
                idx = i
                break
        self.side_idx = min(idx, max(0, len(self._side_buttons) - 1))
        self._update_sidebar_active()

    def _focus_files(self):
        self.focus_panel = "files"
        self._update_sidebar_active()

    # ── Clavier ───────────────────────────────────────────────────────────────

    def _on_key(self, ev):
        # Laisser les champs texte gérer leurs propres touches
        if ev.widget.winfo_class() in ("Entry", "CTkEntry"):
            return

        ctrl  = bool(ev.state & 0x4)
        shift = bool(ev.state & 0x1)
        alt   = bool(ev.state & 0x8)
        k     = ev.keysym

        # Alt+M → menu contextuel
        if k.lower() == "m" and alt and not ctrl and not shift:
            self._show_context_menu()
            return "break"

        # Ctrl+Tab
        if ctrl and not shift and k in ("Tab", "ISO_Left_Tab"):
            self._on_ctrl_tab_event(ev)
            return "break"

        if k == "Escape":
            if self.grab_current():
                return
            self.hide_app()
            return "break"

        # ── Panneau sidebar ──
        if self.focus_panel == "sidebar":
            if k == "Down" and not ctrl:
                self.side_idx = min(self.side_idx + 1, len(self._side_buttons) - 1)
                self._update_sidebar_active()
                return "break"
            if k == "Up" and not ctrl:
                self.side_idx = max(self.side_idx - 1, 0)
                self._update_sidebar_active()
                return "break"
            if k in ("Return", "space") and not ctrl:
                self._sidebar_open_selected()
                return "break"
            if k == "Tab" and not ctrl:
                self._focus_files()
                return "break"
            if ctrl and k == "Up":
                self._go_up()
                return "break"
            if ctrl and k == "Down":
                self._sidebar_open_selected()
                return "break"
            # Toutes les autres touches : ne pas propager (la sidebar a le focus)
            return "break"

        # ── Panneau fichiers ──
        if ctrl and k == "bracketleft":
            self._go_back();  return "break"
        if ctrl and k == "bracketright":
            self._go_fwd();   return "break"
        if ctrl and k == "Up":
            self._go_up();    return "break"
        if ctrl and k == "Down":
            self._open_sel(); return "break"
        if k == "BackSpace" and not ctrl:
            self._go_up();    return "break"

        # Flèches haut/bas : navigation dans la liste
        if k in ("Down", "Up") and not ctrl:
            if not self._display_list:
                return "break"
            prev = set(self.sel)
            cur  = self.last_idx if self.last_idx >= 0 else (
                max(self.sel) if self.sel else -1)
            if k == "Down":
                nx = 0 if cur < 0 else min(cur + 1, len(self._display_list) - 1)
            else:
                nx = max(cur - 1, 0) if cur > 0 else 0
            if shift and cur >= 0:
                lo, hi = min(cur, nx), max(cur, nx)
                self.sel.update(range(lo, hi + 1))
            else:
                self.sel = {nx}
            self._reset_search()
            self.last_idx = nx
            self._update_sel_visual(prev | self.sel)
            self._scroll_to_idx(nx)
            return "break"

        if k == "Return" and not ctrl:
            self._open_sel(); return "break"
        if ctrl and k.lower() == "h":
            self._nav_special("home"); return "break"
        if ctrl and k.lower() == "n":
            self._new_folder(); return "break"
        if ctrl and k.lower() == "r":
            self._reveal(); return "break"
        if k == "Delete":
            self._delete_sel(); return "break"
        if k == "F2":
            self._rename_sel(); return "break"
        if ctrl and k.lower() == "a":
            self._select_all(); return "break"
        if ctrl and k.lower() == "i":
            self._invert_sel(); return "break"
        if ctrl and k.lower() == "x":
            self._cut_sel(); return "break"
        if ctrl and k.lower() == "c":
            self._copy_sel(); return "break"
        if ctrl and k.lower() == "v":
            self._paste(); return "break"
        if ctrl and k.lower() == "d":
            self._nav_drives(); return "break"
        if ctrl and k == "1":
            self._set_view("icons"); return "break"
        if ctrl and k == "2":
            self._set_view("list"); return "break"
        if ctrl and shift and k.lower() == "n":
            self._set_sort("name"); return "break"
        if ctrl and shift and k.lower() == "d":
            self._set_sort("date"); return "break"
        if ctrl and shift and k.lower() == "s":
            self._set_sort("size"); return "break"
        if ctrl and shift and k.lower() == "t":
            self._set_sort("type"); return "break"
        if k == "space" and not ctrl and not shift:
            items = self._get_sel_items()
            if len(items) == 1 and items[0].get("type") != "folder":
                self._preview_file(items[0]["path"])
            else:
                self._do_search(" ")
            return "break"
        if k in ("Menu", ) or (k == "F10" and not ctrl and not shift):
            self._show_context_menu(); return "break"
        if ctrl and k.lower() == "m":
            self._show_context_menu(); return "break"
        if len(ev.char) == 1 and not ctrl and not shift and ev.char.isprintable():
            self._do_search(ev.char.lower()); return "break"

    # ── À propos / menu contextuel ────────────────────────────────────────────

    def _show_about(self):
        about = ctk.CTkToplevel(self)
        about.title("À propos")
        try:
            ico = _ico_path()
            if os.path.isfile(ico):
                from PIL import Image, ImageTk
                img   = Image.open(ico).resize((48, 48), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                lbl   = tk.Label(about, image=photo)
                lbl.image = photo
                lbl.pack(pady=10)
        except Exception:
            pass
        ctk.CTkLabel(about, text="FINDexplorER", font=FONT_LG).pack()
        ctk.CTkLabel(about, text="Version 0.1", font=FONT_SM,
                     text_color=("gray50", "gray55")).pack(pady=4)
        ctk.CTkLabel(about, text="Auteur : Geo", font=FONT_SM,
                     text_color=("gray50", "gray55")).pack()
        ctk.CTkButton(about, text="OK", command=about.destroy).pack(pady=10)

    def _show_context_menu(self):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Ouvrir",     command=self._open_sel)
        menu.add_separator()
        menu.add_command(label="Couper",     command=self._cut_sel)
        menu.add_command(label="Copier",     command=self._copy_sel)
        menu.add_command(label="Coller",     command=self._paste)
        menu.add_separator()
        menu.add_command(label="Supprimer",  command=self._delete_sel)
        menu.add_separator()
        menu.add_command(label="Renommer",   command=self._rename_sel)
        x, y = self.winfo_pointerx(), self.winfo_pointery()
        menu.tk_popup(x, y)
        self.after(100, menu.destroy)


# ── Point d'entrée ────────────────────────────────────────────────────────────

_app_instance = None

def get_app():
    return _app_instance

def run_ui():
    global _app_instance
    ctk.set_appearance_mode("system")
    app = ExplorerApp()
    _app_instance = app
    app.mainloop()
