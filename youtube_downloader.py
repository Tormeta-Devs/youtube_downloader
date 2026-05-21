from __future__ import annotations

import html
import importlib
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import urllib.request
import webbrowser
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from tkinter import filedialog, messagebox
import tkinter as tk
from tkinter import ttk

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


APP_NAME = "YouTube Downloader"
BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.txt"
LANG_DIR = BASE_DIR / "lang"
DEFAULT_LANGUAGE = "es"
SUPPORTED_LANGUAGES = ("es", "en")
SEARCH_LIMIT = 10
THUMBNAIL_SIZE = (92, 52)
AUDIO_FORMATS = ("mp3", "m4a", "aac", "flac", "opus", "vorbis", "wav")
VIDEO_FORMATS = ("mp4", "webm")
ALL_FORMATS = AUDIO_FORMATS + VIDEO_FORMATS

THEMES = {
    "light": {
        "bg": "#f6f7fb",
        "panel": "#ffffff",
        "panel_alt": "#eef2f7",
        "input": "#ffffff",
        "text": "#17202a",
        "muted": "#64748b",
        "line": "#d7dee8",
        "primary": "#2563eb",
        "primary_hover": "#1d4ed8",
        "danger": "#b42318",
        "danger_hover": "#912018",
        "ok": "#047857",
        "ok_hover": "#03694f",
        "youtube": "#ff0033",
        "youtube_hover": "#cc0029",
        "tree": "#ffffff",
        "tree_selected": "#dbeafe",
        "tree_selected_text": "#17202a",
        "log": "#101828",
        "log_text": "#e5e7eb",
        "thumb_bg": "#e5e7eb",
        "thumb_inner": "#cbd5e1",
    },
    "dark": {
        "bg": "#0b1020",
        "panel": "#111827",
        "panel_alt": "#1f2937",
        "input": "#0f172a",
        "text": "#e5e7eb",
        "muted": "#94a3b8",
        "line": "#334155",
        "primary": "#3b82f6",
        "primary_hover": "#60a5fa",
        "danger": "#ef4444",
        "danger_hover": "#dc2626",
        "ok": "#10b981",
        "ok_hover": "#059669",
        "youtube": "#ff0033",
        "youtube_hover": "#ff335c",
        "tree": "#0f172a",
        "tree_selected": "#1d4ed8",
        "tree_selected_text": "#ffffff",
        "log": "#020617",
        "log_text": "#e5e7eb",
        "thumb_bg": "#1f2937",
        "thumb_inner": "#334155",
    },
}
COLORS = THEMES["light"]


FALLBACK_MESSAGES = {
    "es": {
        "window_title": APP_NAME,
        "app_subtitle": "Busca, elige formato y descarga sin salir de la app.",
        "search_placeholder": "Buscar en YouTube",
        "search_button": "Buscar",
        "download_button": "Descargar",
        "directory_button": "Cambiar carpeta",
        "open_folder_button": "Abrir carpeta",
        "copy_url_button": "Copiar URL",
        "open_youtube_button": "YouTube",
        "preview_button": "Vista previa",
        "clear_button": "Limpiar",
        "format_label": "Formato",
        "folder_label": "Carpeta",
        "results_label": "Resultados",
        "activity_label": "Actividad",
        "tools_label": "Herramientas",
        "ready_status": "Listo",
        "searching_status": "Buscando...",
        "downloading_status": "Descargando...",
        "previewing_status": "Preparando vista previa...",
        "preview_ready_status": "Vista previa abierta",
        "preview_error_title": "Error de vista previa",
        "download_complete_status": "Descarga finalizada",
        "search_empty_title": "Busqueda vacia",
        "search_empty_message": "Escribi algo para buscar.",
        "no_results_title": "Sin resultados",
        "no_results_message": "No se encontraron videos para esa busqueda.",
        "select_video": "Seleccion requerida",
        "select_video_message": "Selecciona un video de la lista.",
        "missing_downloader_title": "Falta yt-dlp o youtube-dl",
        "missing_downloader_message": "Falta yt-dlp. Queres instalarlo automaticamente ahora?",
        "installing_downloader_status": "Instalando yt-dlp...",
        "install_downloader_done": "yt-dlp instalado. Ya podes buscar y descargar.",
        "install_downloader_failed": "No se pudo instalar yt-dlp automaticamente.",
        "missing_ffmpeg_title": "Falta FFmpeg",
        "missing_ffmpeg_message": "Instala FFmpeg para convertir audio o combinar video.",
        "download_error_title": "Error de descarga",
        "search_error_title": "Error de busqueda",
        "tools_updated_title": "Herramientas",
        "tools_updated_message": "Proceso de actualizacion terminado.",
        "tools_update_failed": "No se pudo actualizar automaticamente.",
        "check_updates": "Actualizar herramientas",
        "language_settings": "Idioma",
        "language_name_es": "Espanol",
        "language_name_en": "Ingles",
        "downloads": "Descargas",
        "duration_column": "Duracion",
        "title_column": "Titulo",
        "channel_column": "Canal",
        "views_column": "Vistas",
        "thumbnail_column": "Foto",
        "unknown": "Desconocido",
        "ffmpeg": "FFmpeg",
        "downloader": "Motor",
        "not_found": "No encontrado",
        "copied_status": "URL copiada",
        "folder_error_title": "Carpeta no disponible",
        "folder_error_message": "La carpeta elegida no existe o no se puede abrir.",
        "confirm_update_title": "Actualizar herramientas",
        "confirm_update_message": "Se intentara instalar o actualizar yt-dlp y FFmpeg usando winget.",
        "stop_button": "Detener",
        "cancelled_status": "Operacion detenida",
        "thumbnails_disabled": "Pillow no esta instalado; se muestran miniaturas genericas.",
        "install_pillow_title": "Miniaturas",
        "install_pillow_message": "Para ver las fotos hay que instalar Pillow. Queres hacerlo automaticamente?",
        "installing_pillow_status": "Instalando Pillow...",
        "install_pillow_done": "Pillow instalado. Cargando miniaturas...",
        "install_pillow_failed": "No se pudo instalar Pillow automaticamente.",
        "appearance_settings": "Apariencia",
        "theme_light": "Modo claro",
        "theme_dark": "Modo oscuro",
        "toggle_theme": "Cambiar tema",
        "selected_label": "Seleccion actual",
        "no_selection": "Elegi un resultado para ver el detalle.",
        "about_settings": "About",
        "about_app": "Acerca de",
        "app_updates": "Buscar actualizaciones",
        "uninstall_app": "Desinstalar app",
        "installed_only_title": "Instalacion requerida",
        "installed_only_message": "Esta opcion solo funciona cuando la app esta instalada en AppData.",
        "updater_missing_title": "Updater no disponible",
        "updater_missing_message": "No se encontro el actualizador en la carpeta app.",
        "uninstall_confirm_title": "Desinstalar",
        "uninstall_confirm_message": "Se abrira el desinstalador y la app se cerrara.",
        "about_message": "YouTube Downloader\nTormenta-Devs\nRepositorio: Tormeta-Devs/youtube_downloader",
    },
    "en": {
        "window_title": APP_NAME,
        "app_subtitle": "Search, choose a format, and download without leaving the app.",
        "search_placeholder": "Search YouTube",
        "search_button": "Search",
        "download_button": "Download",
        "directory_button": "Change folder",
        "open_folder_button": "Open folder",
        "copy_url_button": "Copy URL",
        "open_youtube_button": "YouTube",
        "preview_button": "Preview",
        "clear_button": "Clear",
        "format_label": "Format",
        "folder_label": "Folder",
        "results_label": "Results",
        "activity_label": "Activity",
        "tools_label": "Tools",
        "ready_status": "Ready",
        "searching_status": "Searching...",
        "downloading_status": "Downloading...",
        "previewing_status": "Preparing preview...",
        "preview_ready_status": "Preview opened",
        "preview_error_title": "Preview error",
        "download_complete_status": "Download complete",
        "search_empty_title": "Empty search",
        "search_empty_message": "Type something to search.",
        "no_results_title": "No results",
        "no_results_message": "No videos were found for that search.",
        "select_video": "Selection required",
        "select_video_message": "Select a video from the list.",
        "missing_downloader_title": "yt-dlp or youtube-dl missing",
        "missing_downloader_message": "yt-dlp is missing. Install it automatically now?",
        "installing_downloader_status": "Installing yt-dlp...",
        "install_downloader_done": "yt-dlp installed. You can search and download now.",
        "install_downloader_failed": "yt-dlp could not be installed automatically.",
        "missing_ffmpeg_title": "FFmpeg missing",
        "missing_ffmpeg_message": "Install FFmpeg to convert audio or merge video.",
        "download_error_title": "Download error",
        "search_error_title": "Search error",
        "tools_updated_title": "Tools",
        "tools_updated_message": "Update process finished.",
        "tools_update_failed": "Automatic update failed.",
        "check_updates": "Update tools",
        "language_settings": "Language",
        "language_name_es": "Spanish",
        "language_name_en": "English",
        "downloads": "Downloads",
        "duration_column": "Duration",
        "title_column": "Title",
        "channel_column": "Channel",
        "views_column": "Views",
        "thumbnail_column": "Cover",
        "unknown": "Unknown",
        "ffmpeg": "FFmpeg",
        "downloader": "Engine",
        "not_found": "Not found",
        "copied_status": "URL copied",
        "folder_error_title": "Folder unavailable",
        "folder_error_message": "The selected folder does not exist or cannot be opened.",
        "confirm_update_title": "Update tools",
        "confirm_update_message": "The app will try to install or update yt-dlp and FFmpeg using winget.",
        "stop_button": "Stop",
        "cancelled_status": "Operation stopped",
        "thumbnails_disabled": "Pillow is not installed; generic thumbnails are shown.",
        "install_pillow_title": "Thumbnails",
        "install_pillow_message": "Pillow is required to show covers. Install it automatically?",
        "installing_pillow_status": "Installing Pillow...",
        "install_pillow_done": "Pillow installed. Loading thumbnails...",
        "install_pillow_failed": "Pillow could not be installed automatically.",
        "appearance_settings": "Appearance",
        "theme_light": "Light mode",
        "theme_dark": "Dark mode",
        "toggle_theme": "Toggle theme",
        "selected_label": "Current selection",
        "no_selection": "Choose a result to see details.",
        "about_settings": "About",
        "about_app": "About",
        "app_updates": "Check for updates",
        "uninstall_app": "Uninstall app",
        "installed_only_title": "Install required",
        "installed_only_message": "This option only works when the app is installed in AppData.",
        "updater_missing_title": "Updater unavailable",
        "updater_missing_message": "The updater was not found inside the app folder.",
        "uninstall_confirm_title": "Uninstall",
        "uninstall_confirm_message": "The uninstaller will open and the app will close.",
        "about_message": "YouTube Downloader\nTormenta-Devs\nRepository: Tormeta-Devs/youtube_downloader",
    },
}


@dataclass
class SearchResult:
    title: str
    url: str
    video_id: str = ""
    channel: str = ""
    duration: int | str | None = None
    views: int | str | None = None
    thumbnail_url: str = ""


class YouTubeDownloaderApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.config = self.load_config()
        self.language = self.config.get("Lang", DEFAULT_LANGUAGE)
        if self.language not in SUPPORTED_LANGUAGES:
            self.language = DEFAULT_LANGUAGE

        self.messages = self.load_messages(self.language)
        self.output_directory = Path(
            self.config.get(
                "Output",
                str(Path.home() / "Downloads"),
            )
        )
        self.selected_format = self.config.get("Format", "mp3")
        if self.selected_format not in ALL_FORMATS:
            self.selected_format = "mp3"
        self.theme_name = self.config.get("Theme", "light")
        if self.theme_name not in THEMES:
            self.theme_name = "light"
        self.colors = THEMES[self.theme_name]
        self.set_global_colors()

        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.results: list[SearchResult] = []
        self.results_generation = 0
        self.thumbnail_images: dict[str, object] = {}
        self.thumbnail_cache: dict[str, bytes] = {}
        self.placeholder_thumbnail: tk.PhotoImage | None = None
        self.download_counter = 0
        self.active_process: subprocess.Popen | None = None
        self.worker_thread: threading.Thread | None = None
        self.current_operation = ""
        self.cancel_requested = False
        self.pillow_install_prompted = False

        self.search_var = tk.StringVar()
        self.folder_var = tk.StringVar(value=str(self.output_directory))
        self.format_var = tk.StringVar(value=self.selected_format)
        self.status_var = tk.StringVar(value=self.t("ready_status"))
        self.tools_var = tk.StringVar()
        self.progress_var = tk.DoubleVar(value=0)
        self.selected_title_var = tk.StringVar(value=self.t("no_selection"))
        self.selected_meta_var = tk.StringVar(value="")

        self.root.title(APP_NAME)
        self.root.geometry("1060x680")
        self.root.minsize(900, 560)
        self.root.configure(bg=self.colors["bg"])
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.setup_styles()
        self.create_menu()
        self.create_layout()
        self.apply_theme()
        self.poll_events()

    def t(self, key: str, fallback: str | None = None) -> str:
        return self.messages.get(key) or FALLBACK_MESSAGES[self.language].get(key, fallback or key)

    def set_global_colors(self) -> None:
        global COLORS
        COLORS = self.colors

    def load_config(self) -> dict[str, str]:
        config: dict[str, str] = {}
        if not CONFIG_FILE.exists():
            return config

        for line in CONFIG_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            config[key.strip()] = value.strip()
        return config

    def save_config(self) -> None:
        self.config["Lang"] = self.language
        self.config["Output"] = str(self.output_directory)
        self.config["Format"] = self.format_var.get()
        self.config["Theme"] = self.theme_name
        lines = [f"{key}: {value}" for key, value in self.config.items()]
        CONFIG_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def load_messages(self, language: str) -> dict[str, str]:
        messages = dict(FALLBACK_MESSAGES.get(language, FALLBACK_MESSAGES[DEFAULT_LANGUAGE]))
        messages_path = LANG_DIR / f"messages_{language}.xml"
        if not messages_path.exists():
            return messages

        try:
            tree = ET.parse(messages_path)
            root = tree.getroot()
            for child in root:
                if child.text:
                    messages[child.tag] = child.text.strip()
        except ET.ParseError:
            return messages
        return messages

    def setup_styles(self) -> None:
        self.set_global_colors()
        colors = self.colors
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        default_font = ("Segoe UI", 10)
        title_font = ("Segoe UI", 20, "bold")
        section_font = ("Segoe UI", 11, "bold")

        self.root.option_add("*Font", default_font)
        self.root.option_add("*tearOff", False)

        style.configure("App.TFrame", background=colors["bg"])
        style.configure("Panel.TFrame", background=colors["panel"])
        style.configure("Soft.TFrame", background=colors["panel_alt"])
        style.configure("Title.TLabel", background=colors["bg"], foreground=colors["text"], font=title_font)
        style.configure("Subtitle.TLabel", background=colors["bg"], foreground=colors["muted"])
        style.configure("Panel.TLabel", background=colors["panel"], foreground=colors["text"])
        style.configure("Muted.TLabel", background=colors["panel"], foreground=colors["muted"])
        style.configure("SoftPanel.TLabel", background=colors["panel_alt"], foreground=colors["text"])
        style.configure("SoftMuted.TLabel", background=colors["panel_alt"], foreground=colors["muted"])
        style.configure("SoftSection.TLabel", background=colors["panel_alt"], foreground=colors["text"], font=section_font)
        style.configure("Section.TLabel", background=colors["panel"], foreground=colors["text"], font=section_font)
        style.configure("Status.TLabel", background=colors["bg"], foreground=colors["muted"])
        style.configure("TButton", padding=(14, 8), background=colors["panel"], foreground=colors["text"])
        style.map("TButton", background=[("active", colors["panel_alt"]), ("disabled", colors["line"])])
        style.configure("Primary.TButton", padding=(16, 8), background=colors["primary"], foreground="#ffffff")
        style.map("Primary.TButton", background=[("active", colors["primary_hover"]), ("disabled", colors["line"])])
        style.configure("Danger.TButton", padding=(16, 8), background=colors["danger"], foreground="#ffffff")
        style.map("Danger.TButton", background=[("active", colors["danger_hover"]), ("disabled", colors["line"])])
        style.configure(
            "TEntry",
            fieldbackground=colors["input"],
            background=colors["input"],
            foreground=colors["text"],
            bordercolor=colors["line"],
            lightcolor=colors["line"],
            insertcolor=colors["text"],
        )
        style.configure(
            "TCombobox",
            fieldbackground=colors["input"],
            background=colors["input"],
            foreground=colors["text"],
            arrowcolor=colors["muted"],
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", colors["input"])],
            foreground=[("readonly", colors["text"])],
        )
        style.configure(
            "Treeview",
            rowheight=62,
            background=colors["tree"],
            fieldbackground=colors["tree"],
            foreground=colors["text"],
            bordercolor=colors["line"],
        )
        style.map(
            "Treeview",
            background=[("selected", colors["tree_selected"])],
            foreground=[("selected", colors["tree_selected_text"])],
        )
        style.configure("Treeview.Heading", padding=(8, 8), background=colors["panel_alt"], foreground=colors["text"])
        style.configure("Horizontal.TProgressbar", background=colors["primary"], troughcolor=colors["panel_alt"])
        style.configure("YouTube.TButton", padding=(16, 8), background=colors["youtube"], foreground="#ffffff")
        style.map("YouTube.TButton", background=[("active", colors["youtube_hover"]), ("disabled", colors["line"])])
        style.configure("Preview.TButton", padding=(16, 8), background=colors["ok"], foreground="#ffffff")
        style.map("Preview.TButton", background=[("active", colors["ok_hover"]), ("disabled", colors["line"])])

    def create_menu(self) -> None:
        self.menu = tk.Menu(self.root)

        self.language_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label=self.t("language_settings"), menu=self.language_menu)

        self.appearance_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label=self.t("appearance_settings"), menu=self.appearance_menu)
        self.appearance_menu.add_command(label=self.t("theme_light"), command=lambda: self.change_theme("light"))
        self.appearance_menu.add_command(label=self.t("theme_dark"), command=lambda: self.change_theme("dark"))

        self.tools_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label=self.t("tools_label"), menu=self.tools_menu)
        self.tools_menu.add_command(label=self.t("check_updates"), command=self.update_tools)

        self.about_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label=self.t("about_settings"), menu=self.about_menu)
        self.about_menu.add_command(label=self.t("about_app"), command=self.show_about)
        self.about_menu.add_command(label=self.t("app_updates"), command=self.check_app_updates)
        self.about_menu.add_separator()
        self.about_menu.add_command(label=self.t("uninstall_app"), command=self.start_uninstall)

        self.root.config(menu=self.menu)
        self.refresh_language_menu()

    def refresh_language_menu(self) -> None:
        self.language_menu.delete(0, tk.END)
        for language in SUPPORTED_LANGUAGES:
            label = self.t(f"language_name_{language}", language.upper())
            self.language_menu.add_command(label=label, command=lambda lang=language: self.change_language(lang))

    def create_layout(self) -> None:
        shell = ttk.Frame(self.root, style="App.TFrame", padding=18)
        shell.pack(fill=tk.BOTH, expand=True)
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(1, weight=1)

        header = ttk.Frame(shell, style="App.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        header.columnconfigure(0, weight=1)

        self.title_label = ttk.Label(header, style="Title.TLabel")
        self.title_label.grid(row=0, column=0, sticky="w")
        self.subtitle_label = ttk.Label(header, style="Subtitle.TLabel")
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(3, 0))
        self.tools_label = ttk.Label(header, textvariable=self.tools_var, style="Status.TLabel")
        self.tools_label.grid(row=0, column=1, sticky="e")
        self.theme_button = ttk.Button(header, command=self.toggle_theme)
        self.theme_button.grid(row=1, column=1, sticky="e", pady=(6, 0))

        body = ttk.Frame(shell, style="Panel.TFrame", padding=16)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(1, weight=1)

        search_bar = ttk.Frame(body, style="Panel.TFrame")
        search_bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        search_bar.columnconfigure(0, weight=1)

        self.search_entry = ttk.Entry(search_bar, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda _event: self.search())

        self.search_button = ttk.Button(search_bar, style="Primary.TButton", command=self.search)
        self.search_button.grid(row=0, column=1, padx=(0, 8))

        self.clear_button = ttk.Button(search_bar, command=self.clear_results)
        self.clear_button.grid(row=0, column=2)

        results_panel = ttk.Frame(body, style="Panel.TFrame")
        results_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 16))
        results_panel.columnconfigure(0, weight=1)
        results_panel.rowconfigure(1, weight=1)

        self.results_label = ttk.Label(results_panel, style="Section.TLabel")
        self.results_label.grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.placeholder_thumbnail = self.create_placeholder_thumbnail()
        columns = ("title", "channel", "duration", "views")
        self.results_tree = ttk.Treeview(results_panel, columns=columns, show="tree headings", selectmode="browse")
        self.results_tree.grid(row=1, column=0, sticky="nsew")
        self.results_tree.heading("#0", text=self.t("thumbnail_column"))
        self.results_tree.heading("title", text=self.t("title_column"))
        self.results_tree.heading("channel", text=self.t("channel_column"))
        self.results_tree.heading("duration", text=self.t("duration_column"))
        self.results_tree.heading("views", text=self.t("views_column"))
        self.results_tree.column("#0", width=112, minwidth=104, stretch=False, anchor=tk.CENTER)
        self.results_tree.column("title", width=360, minwidth=220, stretch=True)
        self.results_tree.column("channel", width=150, minwidth=110)
        self.results_tree.column("duration", width=80, minwidth=70, anchor=tk.CENTER)
        self.results_tree.column("views", width=90, minwidth=80, anchor=tk.E)
        self.results_tree.bind("<Double-1>", lambda _event: self.download())
        self.results_tree.bind("<<TreeviewSelect>>", lambda _event: self.update_selection_panel())

        tree_scroll = ttk.Scrollbar(results_panel, orient=tk.VERTICAL, command=self.results_tree.yview)
        tree_scroll.grid(row=1, column=1, sticky="ns")
        self.results_tree.configure(yscrollcommand=tree_scroll.set)

        side = ttk.Frame(body, style="Panel.TFrame")
        side.grid(row=1, column=1, sticky="nsew")
        side.columnconfigure(0, weight=1)
        side.rowconfigure(9, weight=1)

        self.format_label = ttk.Label(side, style="Section.TLabel")
        self.format_label.grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.format_combo = ttk.Combobox(side, values=ALL_FORMATS, textvariable=self.format_var, state="readonly")
        self.format_combo.grid(row=1, column=0, sticky="ew")
        self.format_combo.bind("<<ComboboxSelected>>", lambda _event: self.save_config())

        self.folder_label = ttk.Label(side, style="Section.TLabel")
        self.folder_label.grid(row=2, column=0, sticky="w", pady=(18, 8))

        folder_box = ttk.Frame(side, style="Panel.TFrame")
        folder_box.grid(row=3, column=0, sticky="ew")
        folder_box.columnconfigure(0, weight=1)

        self.folder_entry = ttk.Entry(folder_box, textvariable=self.folder_var)
        self.folder_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.folder_entry.bind("<FocusOut>", lambda _event: self.sync_folder_from_entry())

        self.directory_button = ttk.Button(folder_box, command=self.select_directory)
        self.directory_button.grid(row=0, column=1)

        actions = ttk.Frame(side, style="Panel.TFrame")
        actions.grid(row=4, column=0, sticky="ew", pady=(16, 0))
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)

        self.download_button = ttk.Button(actions, style="Primary.TButton", command=self.download)
        self.download_button.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.copy_url_button = ttk.Button(actions, command=self.copy_selected_url)
        self.copy_url_button.grid(row=1, column=0, sticky="ew", pady=(8, 0), padx=(0, 4))

        self.open_folder_button = ttk.Button(actions, command=self.open_folder)
        self.open_folder_button.grid(row=1, column=1, sticky="ew", pady=(8, 0), padx=(4, 0))

        self.preview_button = ttk.Button(actions, style="Preview.TButton", command=self.preview_selected_audio)
        self.preview_button.grid(row=2, column=0, sticky="ew", pady=(8, 0), padx=(0, 4))

        self.open_youtube_button = ttk.Button(actions, style="YouTube.TButton", command=self.open_selected_youtube)
        self.open_youtube_button.grid(row=2, column=1, sticky="ew", pady=(8, 0), padx=(4, 0))

        self.stop_button = ttk.Button(actions, style="Danger.TButton", command=self.stop_operation)
        self.stop_button.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        selected_panel = ttk.Frame(side, style="Soft.TFrame", padding=12)
        selected_panel.grid(row=5, column=0, sticky="ew", pady=(18, 0))
        selected_panel.columnconfigure(0, weight=1)

        self.selected_label = ttk.Label(selected_panel, style="SoftSection.TLabel")
        self.selected_label.grid(row=0, column=0, sticky="w")
        self.selected_title_label = ttk.Label(
            selected_panel,
            textvariable=self.selected_title_var,
            style="SoftPanel.TLabel",
            wraplength=330,
        )
        self.selected_title_label.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self.selected_meta_label = ttk.Label(
            selected_panel,
            textvariable=self.selected_meta_var,
            style="SoftMuted.TLabel",
            wraplength=330,
        )
        self.selected_meta_label.grid(row=2, column=0, sticky="ew", pady=(4, 0))

        self.activity_label = ttk.Label(side, style="Section.TLabel")
        self.activity_label.grid(row=6, column=0, sticky="w", pady=(18, 8))

        self.progress_bar = ttk.Progressbar(side, variable=self.progress_var, maximum=100, mode="determinate")
        self.progress_bar.grid(row=7, column=0, sticky="ew")

        self.status_label = ttk.Label(side, textvariable=self.status_var, style="Muted.TLabel")
        self.status_label.grid(row=8, column=0, sticky="ew", pady=(8, 0))

        self.log_box = tk.Text(
            side,
            height=12,
            wrap="word",
            bg=COLORS["log"],
            fg="#e5e7eb",
            insertbackground="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=10,
            state=tk.DISABLED,
        )
        self.log_box.grid(row=9, column=0, sticky="nsew", pady=(12, 0))

        footer = ttk.Frame(shell, style="App.TFrame")
        footer.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        footer.columnconfigure(0, weight=1)

        self.footer_label = ttk.Label(footer, textvariable=self.status_var, style="Status.TLabel")
        self.footer_label.grid(row=0, column=0, sticky="w")

    def update_texts(self) -> None:
        self.root.title(
            f"{self.t('window_title')} | {self.t('downloads')}: {self.download_counter}"
        )
        self.title_label.config(text=self.t("window_title"))
        self.subtitle_label.config(text=self.t("app_subtitle"))
        self.theme_button.config(text=self.t("theme_dark") if self.theme_name == "light" else self.t("theme_light"))
        self.search_button.config(text=self.t("search_button"))
        self.clear_button.config(text=self.t("clear_button"))
        self.results_label.config(text=self.t("results_label"))
        self.format_label.config(text=self.t("format_label"))
        self.folder_label.config(text=self.t("folder_label"))
        self.directory_button.config(text=self.t("directory_button"))
        self.download_button.config(text=self.t("download_button"))
        self.copy_url_button.config(text=self.t("copy_url_button"))
        self.open_folder_button.config(text=self.t("open_folder_button"))
        self.preview_button.config(text=self.t("preview_button"))
        self.open_youtube_button.config(text=self.t("open_youtube_button"))
        self.activity_label.config(text=self.t("activity_label"))
        self.selected_label.config(text=self.t("selected_label"))
        if not self.selected_result():
            self.selected_title_var.set(self.t("no_selection"))
            self.selected_meta_var.set("")
        self.stop_button.config(text=self.t("stop_button"))
        self.results_tree.heading("#0", text=self.t("thumbnail_column"))
        self.results_tree.heading("title", text=self.t("title_column"))
        self.results_tree.heading("channel", text=self.t("channel_column"))
        self.results_tree.heading("duration", text=self.t("duration_column"))
        self.results_tree.heading("views", text=self.t("views_column"))

        self.menu.entryconfigure(0, label=self.t("language_settings"))
        self.menu.entryconfigure(1, label=self.t("appearance_settings"))
        self.menu.entryconfigure(2, label=self.t("tools_label"))
        self.menu.entryconfigure(3, label=self.t("about_settings"))
        self.appearance_menu.entryconfigure(0, label=self.t("theme_light"))
        self.appearance_menu.entryconfigure(1, label=self.t("theme_dark"))
        self.tools_menu.entryconfigure(0, label=self.t("check_updates"))
        self.about_menu.entryconfigure(0, label=self.t("about_app"))
        self.about_menu.entryconfigure(1, label=self.t("app_updates"))
        self.about_menu.entryconfigure(3, label=self.t("uninstall_app"))
        self.refresh_language_menu()
        self.refresh_tool_status()

    def change_language(self, language: str) -> None:
        self.language = language
        self.messages = self.load_messages(language)
        self.status_var.set(self.t("ready_status"))
        self.update_texts()
        self.save_config()

    def toggle_theme(self) -> None:
        self.change_theme("dark" if self.theme_name == "light" else "light")

    def change_theme(self, theme_name: str) -> None:
        if theme_name not in THEMES:
            return
        self.theme_name = theme_name
        self.colors = THEMES[theme_name]
        self.setup_styles()
        self.apply_theme()
        self.save_config()

    def apply_theme(self) -> None:
        self.root.configure(bg=self.colors["bg"])
        self.configure_menu_theme(self.menu)
        self.configure_menu_theme(self.language_menu)
        self.configure_menu_theme(self.appearance_menu)
        self.configure_menu_theme(self.tools_menu)
        self.configure_menu_theme(self.about_menu)
        if hasattr(self, "log_box"):
            self.log_box.config(
                bg=self.colors["log"],
                fg=self.colors["log_text"],
                insertbackground=self.colors["log_text"],
            )
        if hasattr(self, "placeholder_thumbnail"):
            self.placeholder_thumbnail = self.create_placeholder_thumbnail()
            for item in self.results_tree.get_children():
                if item not in self.thumbnail_images:
                    self.results_tree.item(item, image=self.placeholder_thumbnail)
        self.update_texts()

    def configure_menu_theme(self, menu: tk.Menu) -> None:
        try:
            menu.config(
                bg=self.colors["panel"],
                fg=self.colors["text"],
                activebackground=self.colors["panel_alt"],
                activeforeground=self.colors["text"],
                borderwidth=0,
            )
        except tk.TclError:
            pass

    def refresh_tool_status(self) -> None:
        downloader_name = self.downloader_display_name()
        ffmpeg_version = self.ffmpeg_version()
        self.tools_var.set(
            f"{self.t('downloader')}: {downloader_name}   |   {self.t('ffmpeg')}: {ffmpeg_version}"
        )

    def is_installed_copy(self) -> bool:
        return (BASE_DIR / "app" / "install.json").exists()

    def show_about(self) -> None:
        install_text = f"\n\nInstall path:\n{BASE_DIR}" if self.is_installed_copy() else f"\n\nDev path:\n{BASE_DIR}"
        messagebox.showinfo(self.t("about_app"), self.t("about_message") + install_text)

    def check_app_updates(self) -> None:
        updater = BASE_DIR / "app" / "updater.py"
        if not self.is_installed_copy():
            messagebox.showinfo(self.t("installed_only_title"), self.t("installed_only_message"))
            return
        if not updater.exists():
            messagebox.showerror(self.t("updater_missing_title"), self.t("updater_missing_message"))
            return
        subprocess.Popen(
            [sys.executable, str(updater), "--gui"],
            cwd=str(BASE_DIR),
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )

    def start_uninstall(self) -> None:
        uninstaller = BASE_DIR / "app" / "uninstall.py"
        if not self.is_installed_copy():
            messagebox.showinfo(self.t("installed_only_title"), self.t("installed_only_message"))
            return
        if not uninstaller.exists():
            messagebox.showerror(self.t("updater_missing_title"), self.t("updater_missing_message"))
            return
        if not messagebox.askyesno(self.t("uninstall_confirm_title"), self.t("uninstall_confirm_message")):
            return
        subprocess.Popen(
            [sys.executable, str(uninstaller), "--from-app"],
            cwd=str(BASE_DIR),
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        self.root.after(500, self.close)

    def downloader_command(self) -> list[str] | None:
        if shutil.which("yt-dlp"):
            return ["yt-dlp"]
        if shutil.which("youtube-dl"):
            return ["youtube-dl"]
        if self.module_available("yt_dlp"):
            return [sys.executable, "-m", "yt_dlp"]
        if self.module_available("youtube_dl"):
            return [sys.executable, "-m", "youtube_dl"]
        return None

    def downloader_display_name(self) -> str:
        command = self.downloader_command()
        if not command:
            return self.t("not_found")
        if command[:3] == [sys.executable, "-m", "yt_dlp"]:
            return "yt-dlp"
        if command[:3] == [sys.executable, "-m", "youtube_dl"]:
            return "youtube-dl"
        return Path(command[0]).name

    def module_available(self, module_name: str) -> bool:
        try:
            __import__(module_name)
        except Exception:
            return False
        return True

    def ffmpeg_version(self) -> str:
        if not shutil.which("ffmpeg"):
            return self.t("not_found")
        try:
            completed = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=4,
                startupinfo=self.startupinfo(),
            )
        except Exception:
            return self.t("unknown")

        first_line = (completed.stdout or "").splitlines()[0] if completed.stdout else ""
        match = re.search(r"ffmpeg version\s+([^\s]+)", first_line)
        return match.group(1) if match else self.t("unknown")

    def startupinfo(self) -> subprocess.STARTUPINFO | None:
        if os.name != "nt":
            return None
        info = subprocess.STARTUPINFO()
        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        return info

    def set_busy(self, busy: bool, operation: str = "") -> None:
        self.current_operation = operation if busy else ""
        if busy:
            self.cancel_requested = False
        state = tk.DISABLED if busy else tk.NORMAL
        readonly = tk.DISABLED if busy else "readonly"
        self.search_button.config(state=state)
        self.clear_button.config(state=state)
        self.download_button.config(state=state)
        self.directory_button.config(state=state)
        self.copy_url_button.config(state=state)
        self.open_folder_button.config(state=state)
        self.preview_button.config(state=state)
        self.open_youtube_button.config(state=state)
        self.format_combo.config(state=readonly)
        self.stop_button.config(state=tk.NORMAL if busy else tk.DISABLED)
        if busy:
            self.progress_var.set(0)
        else:
            self.active_process = None

    def search(self) -> None:
        query = self.search_var.get().strip()
        if not query:
            messagebox.showinfo(self.t("search_empty_title"), self.t("search_empty_message"))
            return

        command = self.downloader_command()
        if not command:
            self.offer_downloader_install()
            return

        self.clear_results(clear_search=False)
        self.log(self.t("searching_status"))
        self.status_var.set(self.t("searching_status"))
        self.set_busy(True, "search")
        self.progress_bar.config(mode="indeterminate")
        self.progress_bar.start(12)

        args = command + [
            "--dump-single-json",
            "--flat-playlist",
            "--ignore-errors",
            "--no-warnings",
            f"ytsearch{SEARCH_LIMIT}:{query}",
        ]
        self.worker_thread = threading.Thread(target=self.search_worker, args=(args,), daemon=True)
        self.worker_thread.start()

    def search_worker(self, args: list[str]) -> None:
        try:
            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                startupinfo=self.startupinfo(),
            )
            self.active_process = process
            stdout, stderr = process.communicate()
            if self.cancel_requested:
                self.events.put(("cancelled", None))
                return
            if process.returncode != 0:
                self.events.put(("error", (self.t("search_error_title"), stderr.strip() or stdout.strip())))
                return

            results = self.parse_search_results(stdout)
            self.events.put(("search_done", results))
        except Exception as exc:
            self.events.put(("error", (self.t("search_error_title"), str(exc))))

    def parse_search_results(self, output: str) -> list[SearchResult]:
        results: list[SearchResult] = []
        seen_urls: set[str] = set()

        def add_result(data: dict) -> None:
            title = data.get("title") or self.t("unknown")
            video_id = data.get("id") or ""
            url = data.get("webpage_url") or data.get("url") or ""
            if url and not str(url).startswith("http"):
                video_id = video_id or self.extract_video_id(str(url)) or str(url)
                url = f"https://www.youtube.com/watch?v={video_id}"
            elif video_id and not str(url).startswith("http"):
                url = f"https://www.youtube.com/watch?v={video_id}"
            if not video_id:
                video_id = self.extract_video_id(str(url))
            if not url or url in seen_urls:
                return
            seen_urls.add(url)

            results.append(
                SearchResult(
                    title=title,
                    url=url,
                    video_id=video_id,
                    channel=data.get("uploader") or data.get("channel") or "",
                    duration=data.get("duration"),
                    views=data.get("view_count"),
                    thumbnail_url=self.best_thumbnail_url(data, video_id),
                )
            )

        for line in output.splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            entries = data.get("entries")
            if isinstance(entries, list):
                for entry in entries:
                    if isinstance(entry, dict):
                        add_result(entry)
            else:
                add_result(data)
        return results[:SEARCH_LIMIT]

    def show_results(self, results: list[SearchResult]) -> None:
        self.results_generation += 1
        generation = self.results_generation
        self.results = results
        self.thumbnail_images.clear()
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        for index, result in enumerate(results):
            self.results_tree.insert(
                "",
                tk.END,
                iid=str(index),
                text="",
                image=self.placeholder_thumbnail,
                values=(
                    result.title,
                    result.channel or self.t("unknown"),
                    self.format_duration(result.duration),
                    self.format_number(result.views),
                ),
            )

        if results:
            self.results_tree.selection_set("0")
            self.results_tree.focus("0")
            self.update_selection_panel()
            self.log(f"{len(results)} {self.t('results_label').lower()}")
            self.status_var.set(self.t("ready_status"))
            self.load_result_thumbnails(results, generation)
        else:
            messagebox.showinfo(self.t("no_results_title"), self.t("no_results_message"))
            self.status_var.set(self.t("no_results_title"))

    def selected_result(self) -> SearchResult | None:
        selection = self.results_tree.selection()
        if not selection:
            return None
        try:
            return self.results[int(selection[0])]
        except (ValueError, IndexError):
            return None

    def update_selection_panel(self) -> None:
        result = self.selected_result()
        if not result:
            self.selected_title_var.set(self.t("no_selection"))
            self.selected_meta_var.set("")
            return

        duration = self.format_duration(result.duration)
        views = self.format_number(result.views)
        parts = []
        if result.channel:
            parts.append(result.channel)
        if duration != "-":
            parts.append(duration)
        if views != "-":
            parts.append(f"{views} {self.t('views_column').lower()}")

        self.selected_title_var.set(result.title)
        self.selected_meta_var.set("  |  ".join(parts))

    def download(self) -> None:
        result = self.selected_result()
        if not result:
            messagebox.showerror(self.t("select_video"), self.t("select_video_message"))
            return

        command = self.downloader_command()
        if not command:
            self.offer_downloader_install()
            return

        self.sync_folder_from_entry(show_errors=True)
        self.output_directory.mkdir(parents=True, exist_ok=True)

        selected_format = self.format_var.get() or "mp3"
        if not shutil.which("ffmpeg"):
            messagebox.showerror(self.t("missing_ffmpeg_title"), self.t("missing_ffmpeg_message"))
            return

        template = str(self.output_directory / "%(title)s.%(ext)s")

        args = command + ["--newline", "-o", template]
        if selected_format in AUDIO_FORMATS:
            args += ["-x", "--audio-format", selected_format, "--audio-quality", "0"]
        elif selected_format == "mp4":
            args += ["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "--merge-output-format", "mp4"]
        else:
            args += ["-f", "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best", "--merge-output-format", "webm"]
        args.append(result.url)

        self.progress_bar.stop()
        self.progress_bar.config(mode="determinate")
        self.progress_var.set(0)
        self.log(f"{self.t('downloading_status')} {result.title}")
        self.status_var.set(self.t("downloading_status"))
        self.set_busy(True, "download")
        self.worker_thread = threading.Thread(target=self.download_worker, args=(args,), daemon=True)
        self.worker_thread.start()

    def download_worker(self, args: list[str]) -> None:
        try:
            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                startupinfo=self.startupinfo(),
            )
            self.active_process = process
            assert process.stdout is not None

            for line in process.stdout:
                clean_line = line.strip()
                if clean_line:
                    self.events.put(("log", clean_line))
                    percent = self.extract_percent(clean_line)
                    if percent is not None:
                        self.events.put(("progress", percent))

            return_code = process.wait()
            if self.cancel_requested:
                self.events.put(("cancelled", None))
            elif return_code == 0:
                self.events.put(("download_done", None))
            elif return_code < 0:
                self.events.put(("cancelled", None))
            else:
                self.events.put(("error", (self.t("download_error_title"), f"Codigo de salida: {return_code}")))
        except Exception as exc:
            self.events.put(("error", (self.t("download_error_title"), str(exc))))

    def stop_operation(self) -> None:
        self.cancel_requested = True
        process = self.active_process
        if process and process.poll() is None:
            process.terminate()
            self.log(self.t("cancelled_status"))
            self.status_var.set(self.t("cancelled_status"))

    def poll_events(self) -> None:
        try:
            while True:
                event, payload = self.events.get_nowait()
                if event == "search_done":
                    self.progress_bar.stop()
                    self.progress_bar.config(mode="determinate")
                    self.set_busy(False)
                    self.show_results(payload)  # type: ignore[arg-type]
                elif event == "download_done":
                    self.set_busy(False)
                    self.download_counter += 1
                    self.progress_var.set(100)
                    self.status_var.set(self.t("download_complete_status"))
                    self.log(self.t("download_complete_status"))
                    self.update_texts()
                elif event == "cancelled":
                    self.progress_bar.stop()
                    self.set_busy(False)
                    self.status_var.set(self.t("cancelled_status"))
                elif event == "error":
                    self.progress_bar.stop()
                    self.set_busy(False)
                    title, detail = payload  # type: ignore[misc]
                    self.status_var.set(title)
                    self.log(str(detail))
                    messagebox.showerror(title, str(detail) or title)
                elif event == "log":
                    self.log(str(payload))
                elif event == "progress":
                    self.progress_var.set(float(payload))
                elif event == "tools_done":
                    self.progress_bar.stop()
                    self.progress_bar.config(mode="determinate")
                    self.set_busy(False)
                    self.refresh_tool_status()
                    self.status_var.set(self.t("tools_updated_message"))
                    self.log(self.t("tools_updated_message"))
                    messagebox.showinfo(self.t("tools_updated_title"), self.t("tools_updated_message"))
                elif event == "downloader_installed":
                    self.progress_bar.stop()
                    self.progress_bar.config(mode="determinate")
                    self.set_busy(False)
                    self.refresh_tool_status()
                    self.status_var.set(self.t("install_downloader_done"))
                    self.log(self.t("install_downloader_done"))
                    messagebox.showinfo(self.t("missing_downloader_title"), self.t("install_downloader_done"))
                elif event == "thumbnail":
                    generation, index, image_bytes = payload  # type: ignore[misc]
                    self.apply_thumbnail(int(generation), int(index), image_bytes)
                elif event == "pillow_installed":
                    self.progress_bar.stop()
                    self.progress_bar.config(mode="determinate")
                    self.set_busy(False)
                    generation = int(payload)
                    self.reload_pillow()
                    self.status_var.set(self.t("install_pillow_done"))
                    self.log(self.t("install_pillow_done"))
                    if generation == self.results_generation:
                        self.load_result_thumbnails(self.results, generation)
                elif event == "preview_ready":
                    result, stream_url = payload  # type: ignore[misc]
                    self.progress_bar.stop()
                    self.progress_bar.config(mode="determinate")
                    self.set_busy(False)
                    self.open_preview_player(result, str(stream_url))
                    self.status_var.set(self.t("preview_ready_status"))
                    self.log(self.t("preview_ready_status"))
        except queue.Empty:
            pass

        self.root.after(100, self.poll_events)

    def clear_results(self, clear_search: bool = True) -> None:
        self.results_generation += 1
        if clear_search:
            self.search_var.set("")
        self.results.clear()
        self.selected_title_var.set(self.t("no_selection"))
        self.selected_meta_var.set("")
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.progress_var.set(0)
        self.status_var.set(self.t("ready_status"))

    def select_directory(self) -> None:
        selected = filedialog.askdirectory(initialdir=str(self.output_directory))
        if selected:
            self.output_directory = Path(selected)
            self.folder_var.set(str(self.output_directory))
            self.save_config()

    def sync_folder_from_entry(self, show_errors: bool = False) -> None:
        value = self.folder_var.get().strip()
        if not value:
            self.folder_var.set(str(self.output_directory))
            return

        folder = Path(value).expanduser()
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except OSError:
            if show_errors:
                messagebox.showerror(self.t("folder_error_title"), self.t("folder_error_message"))
            self.folder_var.set(str(self.output_directory))
            return

        self.output_directory = folder
        self.folder_var.set(str(folder))
        self.save_config()

    def open_folder(self) -> None:
        self.sync_folder_from_entry()
        if not self.output_directory.exists():
            messagebox.showerror(self.t("folder_error_title"), self.t("folder_error_message"))
            return

        try:
            if os.name == "nt":
                os.startfile(str(self.output_directory))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(self.output_directory)])
            else:
                subprocess.Popen(["xdg-open", str(self.output_directory)])
        except Exception:
            messagebox.showerror(self.t("folder_error_title"), self.t("folder_error_message"))

    def copy_selected_url(self) -> None:
        result = self.selected_result()
        if not result:
            messagebox.showerror(self.t("select_video"), self.t("select_video_message"))
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(result.url)
        self.status_var.set(self.t("copied_status"))

    def preview_selected_audio(self) -> None:
        result = self.selected_result()
        if not result:
            messagebox.showerror(self.t("select_video"), self.t("select_video_message"))
            return

        command = self.downloader_command()
        if not command:
            self.offer_downloader_install()
            return

        self.log(f"{self.t('previewing_status')} {result.title}")
        self.status_var.set(self.t("previewing_status"))
        self.set_busy(True, "preview")
        self.progress_bar.config(mode="indeterminate")
        self.progress_bar.start(12)

        args = command + [
            "-g",
            "-f",
            "bestaudio/best",
            "--no-warnings",
            result.url,
        ]
        self.worker_thread = threading.Thread(target=self.preview_worker, args=(args, result), daemon=True)
        self.worker_thread.start()

    def preview_worker(self, args: list[str], result: SearchResult) -> None:
        try:
            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                startupinfo=self.startupinfo(),
            )
            self.active_process = process
            stdout, stderr = process.communicate()
            if self.cancel_requested:
                self.events.put(("cancelled", None))
                return
            if process.returncode != 0:
                self.events.put(("error", (self.t("preview_error_title"), stderr.strip() or stdout.strip())))
                return

            stream_url = self.first_stream_url(stdout)
            if not stream_url:
                self.events.put(("error", (self.t("preview_error_title"), stderr.strip() or self.t("preview_error_title"))))
                return

            self.events.put(("preview_ready", (result, stream_url)))
        except Exception as exc:
            self.events.put(("error", (self.t("preview_error_title"), str(exc))))

    def first_stream_url(self, output: str) -> str:
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("http://") or line.startswith("https://"):
                return line
        return ""

    def open_preview_player(self, result: SearchResult, stream_url: str) -> None:
        title = html.escape(result.title)
        stream = html.escape(stream_url, quote=True)
        youtube_url = html.escape(result.url, quote=True)
        page = Path(tempfile.gettempdir()) / "youtube_downloader_preview.html"
        page.write_text(
            f"""<!doctype html>
<html lang="{html.escape(self.language)}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: #101828;
      color: #f8fafc;
      font-family: Segoe UI, Arial, sans-serif;
    }}
    main {{
      width: min(680px, calc(100vw - 32px));
      background: #ffffff;
      color: #17202a;
      border-radius: 14px;
      padding: 24px;
      box-shadow: 0 22px 70px rgba(0, 0, 0, .35);
    }}
    h1 {{
      margin: 0 0 16px;
      font-size: 22px;
      line-height: 1.25;
    }}
    audio {{
      width: 100%;
      margin: 8px 0 18px;
    }}
    a {{
      color: #2563eb;
      font-weight: 600;
    }}
  </style>
</head>
<body>
  <main>
    <h1>{title}</h1>
    <audio controls autoplay src="{stream}"></audio>
    <a href="{youtube_url}" target="_blank" rel="noreferrer">YouTube</a>
  </main>
</body>
</html>
""",
            encoding="utf-8",
        )
        webbrowser.open(page.as_uri(), new=2)

    def open_selected_youtube(self) -> None:
        result = self.selected_result()
        if not result:
            messagebox.showerror(self.t("select_video"), self.t("select_video_message"))
            return
        webbrowser.open(result.url, new=2)

    def offer_downloader_install(self) -> None:
        if not messagebox.askyesno(self.t("missing_downloader_title"), self.t("missing_downloader_message")):
            return

        self.log(self.t("installing_downloader_status"))
        self.status_var.set(self.t("installing_downloader_status"))
        self.set_busy(True, "install_downloader")
        self.progress_bar.config(mode="indeterminate")
        self.progress_bar.start(12)
        self.worker_thread = threading.Thread(target=self.install_downloader_worker, daemon=True)
        self.worker_thread.start()

    def install_downloader_worker(self) -> None:
        args = [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"]
        try:
            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                startupinfo=self.startupinfo(),
            )
            self.active_process = process
            assert process.stdout is not None
            for line in process.stdout:
                clean_line = line.strip()
                if clean_line:
                    self.events.put(("log", clean_line))

            return_code = process.wait()
            if self.cancel_requested:
                self.events.put(("cancelled", None))
            elif return_code == 0:
                self.events.put(("downloader_installed", None))
            else:
                self.events.put(
                    (
                        "error",
                        (
                            self.t("missing_downloader_title"),
                            f"{self.t('install_downloader_failed')} Codigo de salida: {return_code}",
                        ),
                    )
                )
        except Exception as exc:
            self.events.put(("error", (self.t("missing_downloader_title"), str(exc))))

    def update_tools(self) -> None:
        if not shutil.which("winget"):
            messagebox.showerror(self.t("tools_updated_title"), self.t("tools_update_failed"))
            return

        if not messagebox.askyesno(self.t("confirm_update_title"), self.t("confirm_update_message")):
            return

        self.log(self.t("check_updates"))
        self.status_var.set(self.t("check_updates"))
        self.set_busy(True, "tools")
        self.progress_bar.config(mode="indeterminate")
        self.progress_bar.start(12)
        self.worker_thread = threading.Thread(target=self.update_tools_worker, daemon=True)
        self.worker_thread.start()

    def update_tools_worker(self) -> None:
        commands = [
            ["winget", "install", "--id", "yt-dlp.yt-dlp", "-e", "--accept-package-agreements", "--accept-source-agreements"],
            ["winget", "install", "--id", "Gyan.FFmpeg", "-e", "--accept-package-agreements", "--accept-source-agreements"],
        ]
        try:
            for args in commands:
                if self.cancel_requested:
                    self.events.put(("cancelled", None))
                    return
                process = subprocess.Popen(
                    args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    startupinfo=self.startupinfo(),
                )
                self.active_process = process
                assert process.stdout is not None
                for line in process.stdout:
                    clean_line = line.strip()
                    if clean_line:
                        self.events.put(("log", clean_line))
                process.wait()
                if self.cancel_requested:
                    self.events.put(("cancelled", None))
                    return
            self.events.put(("tools_done", None))
        except Exception as exc:
            self.events.put(("error", (self.t("tools_updated_title"), str(exc))))

    def create_placeholder_thumbnail(self) -> tk.PhotoImage:
        image = tk.PhotoImage(width=THUMBNAIL_SIZE[0], height=THUMBNAIL_SIZE[1])
        image.put(self.colors["thumb_bg"], to=(0, 0, THUMBNAIL_SIZE[0], THUMBNAIL_SIZE[1]))
        image.put(self.colors["thumb_inner"], to=(2, 2, THUMBNAIL_SIZE[0] - 2, THUMBNAIL_SIZE[1] - 2))
        play_left = THUMBNAIL_SIZE[0] // 2 - 7
        play_top = THUMBNAIL_SIZE[1] // 2 - 10
        image.put(self.colors["youtube"], to=(play_left - 7, play_top, play_left + 18, play_top + 20))
        image.put("#ffffff", to=(play_left + 1, play_top + 5, play_left + 6, play_top + 15))
        image.put("#ffffff", to=(play_left + 6, play_top + 8, play_left + 11, play_top + 12))
        return image

    def best_thumbnail_url(self, data: dict, video_id: str) -> str:
        direct = data.get("thumbnail")
        if isinstance(direct, str) and direct.startswith("http"):
            return direct

        thumbnails = data.get("thumbnails")
        if isinstance(thumbnails, list):
            urls = [
                thumbnail.get("url")
                for thumbnail in thumbnails
                if isinstance(thumbnail, dict) and isinstance(thumbnail.get("url"), str)
            ]
            if urls:
                return urls[-1]

        if video_id:
            return f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg"
        return ""

    def extract_video_id(self, url: str) -> str:
        patterns = (
            r"[?&]v=([A-Za-z0-9_-]{6,})",
            r"youtu\.be/([A-Za-z0-9_-]{6,})",
            r"/shorts/([A-Za-z0-9_-]{6,})",
            r"/embed/([A-Za-z0-9_-]{6,})",
        )
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return ""

    def load_result_thumbnails(self, results: list[SearchResult], generation: int) -> None:
        if Image is None or ImageTk is None:
            if not self.pillow_install_prompted:
                self.pillow_install_prompted = True
                if messagebox.askyesno(self.t("install_pillow_title"), self.t("install_pillow_message")):
                    self.install_pillow(generation)
                    return
            self.log(self.t("thumbnails_disabled"))
            return

        worker = threading.Thread(target=self.thumbnail_worker, args=(list(enumerate(results)), generation), daemon=True)
        worker.start()

    def install_pillow(self, generation: int) -> None:
        self.log(self.t("installing_pillow_status"))
        self.status_var.set(self.t("installing_pillow_status"))
        self.set_busy(True, "install_pillow")
        self.progress_bar.config(mode="indeterminate")
        self.progress_bar.start(12)
        self.worker_thread = threading.Thread(target=self.install_pillow_worker, args=(generation,), daemon=True)
        self.worker_thread.start()

    def install_pillow_worker(self, generation: int) -> None:
        args = [sys.executable, "-m", "pip", "install", "--upgrade", "Pillow"]
        try:
            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                startupinfo=self.startupinfo(),
            )
            self.active_process = process
            assert process.stdout is not None
            for line in process.stdout:
                clean_line = line.strip()
                if clean_line:
                    self.events.put(("log", clean_line))

            return_code = process.wait()
            if self.cancel_requested:
                self.events.put(("cancelled", None))
            elif return_code == 0:
                self.events.put(("pillow_installed", generation))
            else:
                self.events.put(
                    (
                        "error",
                        (
                            self.t("install_pillow_title"),
                            f"{self.t('install_pillow_failed')} Codigo de salida: {return_code}",
                        ),
                    )
                )
        except Exception as exc:
            self.events.put(("error", (self.t("install_pillow_title"), str(exc))))

    def reload_pillow(self) -> None:
        global Image, ImageTk
        try:
            Image = importlib.import_module("PIL.Image")
            ImageTk = importlib.import_module("PIL.ImageTk")
        except Exception:
            Image = None
            ImageTk = None

    def thumbnail_worker(self, indexed_results: list[tuple[int, SearchResult]], generation: int) -> None:
        for index, result in indexed_results:
            if self.cancel_requested:
                return
            if not result.thumbnail_url:
                continue

            try:
                image_bytes = self.thumbnail_cache.get(result.thumbnail_url)
                if image_bytes is None:
                    request = urllib.request.Request(
                        result.thumbnail_url,
                        headers={"User-Agent": "Mozilla/5.0"},
                    )
                    with urllib.request.urlopen(request, timeout=8) as response:
                        image_bytes = response.read()
                    self.thumbnail_cache[result.thumbnail_url] = image_bytes
                self.events.put(("thumbnail", (generation, index, image_bytes)))
            except Exception:
                continue

    def apply_thumbnail(self, generation: int, index: int, image_bytes: bytes) -> None:
        if generation != self.results_generation:
            return
        if Image is None or ImageTk is None:
            return
        item_id = str(index)
        if not self.results_tree.exists(item_id):
            return

        try:
            with Image.open(BytesIO(image_bytes)) as source:
                source.thumbnail(THUMBNAIL_SIZE)
                canvas = Image.new("RGB", THUMBNAIL_SIZE, "#e5e7eb")
                left = (THUMBNAIL_SIZE[0] - source.width) // 2
                top = (THUMBNAIL_SIZE[1] - source.height) // 2
                canvas.paste(source.convert("RGB"), (left, top))
                image = ImageTk.PhotoImage(canvas)
        except Exception:
            return

        self.thumbnail_images[item_id] = image
        self.results_tree.item(item_id, image=image)

    def log(self, message: str) -> None:
        self.log_box.config(state=tk.NORMAL)
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state=tk.DISABLED)

    def extract_percent(self, line: str) -> float | None:
        match = re.search(r"(\d+(?:\.\d+)?)%", line)
        if not match:
            return None
        try:
            return min(100.0, max(0.0, float(match.group(1))))
        except ValueError:
            return None

    def format_duration(self, seconds: int | str | None) -> str:
        if not seconds:
            return "-"
        if isinstance(seconds, str):
            return seconds if not seconds.isdigit() else self.format_duration(int(seconds))
        minutes, second = divmod(int(seconds), 60)
        hours, minute = divmod(minutes, 60)
        if hours:
            return f"{hours}:{minute:02d}:{second:02d}"
        return f"{minute}:{second:02d}"

    def format_number(self, value: int | str | None) -> str:
        if value is None:
            return "-"
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return "-"
            if not value.isdigit():
                return value
            value = int(value)
        return f"{value:,}".replace(",", ".")

    def close(self) -> None:
        process = self.active_process
        if process and process.poll() is None:
            process.terminate()
        self.save_config()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    app.stop_button.config(state=tk.DISABLED)
    root.mainloop()


if __name__ == "__main__":
    main()
