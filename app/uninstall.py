from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from tkinter import messagebox
import tkinter as tk


INSTALL_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = INSTALL_ROOT / "app"
METADATA_FILE = APP_DIR / "install.json"
UNINSTALL_KEY = r"HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\YouTubeDownloader"


def load_metadata() -> dict:
    if not METADATA_FILE.exists():
        return {}
    try:
        return json.loads(METADATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def remove_registry_entry() -> None:
    if os.name != "nt":
        return
    subprocess.run(["reg", "delete", UNINSTALL_KEY, "/f"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def cleanup_shortcuts(metadata: dict) -> None:
    for key in ("desktop_shortcut", "start_menu_shortcut"):
        value = metadata.get(key)
        if value:
            try:
                Path(value).unlink(missing_ok=True)
            except Exception:
                pass


def run_delayed_cleanup(remove_install_dir: bool, remove_ffmpeg: bool) -> None:
    script_path = Path(tempfile.gettempdir()) / "youtube_downloader_uninstall.ps1"
    install_path = str(INSTALL_ROOT)
    current_pid = os.getpid()
    remove_dir_line = f"Remove-Item -LiteralPath '{install_path}' -Recurse -Force -ErrorAction SilentlyContinue" if remove_install_dir else ""
    ffmpeg_line = "winget uninstall --id Gyan.FFmpeg -e --silent --accept-source-agreements" if remove_ffmpeg else ""
    script_path.write_text(
        f"""
$ErrorActionPreference = 'SilentlyContinue'
Start-Sleep -Seconds 2
Wait-Process -Id {current_pid} -Timeout 20
{ffmpeg_line}
{remove_dir_line}
Remove-Item -LiteralPath $MyInvocation.MyCommand.Path -Force
""",
        encoding="utf-8",
    )
    subprocess.Popen(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )


def main() -> int:
    root = tk.Tk()
    root.withdraw()

    metadata = load_metadata()
    if not messagebox.askyesno("Desinstalar YouTube Downloader", "Queres desinstalar YouTube Downloader?"):
        root.destroy()
        return 0

    remove_ffmpeg = messagebox.askyesno(
        "FFmpeg",
        "Queres intentar desinstalar FFmpeg tambien? Recomendado: No, porque puede estar usado por otros programas.",
    )
    keep_files = messagebox.askyesno(
        "Archivos de la app",
        "Queres conservar la carpeta instalada en AppData? Si elegis No, tambien se eliminan las dependencias Python del entorno local de la app.",
    )

    cleanup_shortcuts(metadata)
    remove_registry_entry()
    run_delayed_cleanup(remove_install_dir=not keep_files, remove_ffmpeg=remove_ffmpeg)
    messagebox.showinfo("Desinstalador", "Desinstalacion iniciada. La carpeta se limpiara cuando se cierren los procesos.")
    root.destroy()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
