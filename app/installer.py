from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from tkinter import messagebox
import tkinter as tk


APP_NAME = "YouTube Downloader"
PUBLISHER = "Tormenta-Devs"
REPOSITORY = "Tormeta-Devs/youtube_downloader"
BRANCH = "main"
INSTALL_ROOT = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "TormentaDevs" / "YouTubeDownloader"
VENV_DIR = INSTALL_ROOT / "venv"
APP_DIR = INSTALL_ROOT / "app"
METADATA_FILE = APP_DIR / "install.json"


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def source_root() -> Path:
    if is_frozen():
        return Path(sys._MEIPASS) / "payload"  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[1]


def run(args: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        check=check,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def find_python() -> str | None:
    if not is_frozen() and Path(sys.executable).exists():
        return sys.executable

    candidates = [
        ["py", "-3", "-c", "import sys; print(sys.executable)"],
        ["python", "-c", "import sys; print(sys.executable)"],
    ]
    for args in candidates:
        try:
            completed = subprocess.run(args, capture_output=True, text=True, timeout=10)
            if completed.returncode == 0:
                executable = completed.stdout.strip().splitlines()[-1]
                if executable and Path(executable).exists():
                    return executable
        except Exception:
            continue
    return None


def install_python_if_missing() -> str:
    python = find_python()
    if python:
        return python

    if not command_exists("winget"):
        raise RuntimeError("No se encontro Python ni winget para instalarlo automaticamente.")

    if not messagebox.askyesno("Python", "No se encontro Python. Queres instalar Python 3 con winget?"):
        raise RuntimeError("Python es necesario para instalar la app.")

    run(["winget", "install", "--id", "Python.Python.3.12", "-e", "--accept-package-agreements", "--accept-source-agreements"])
    python = find_python()
    if not python:
        raise RuntimeError("Python se instalo, pero no se pudo localizar en PATH. Reinicia la terminal o Windows e intenta de nuevo.")
    return python


def copy_payload() -> None:
    source = source_root()
    INSTALL_ROOT.mkdir(parents=True, exist_ok=True)
    APP_DIR.mkdir(parents=True, exist_ok=True)

    files = ("youtube_downloader.py", "requirements.txt", "README.md")
    for name in files:
        src = source / name
        if src.exists():
            shutil.copy2(src, INSTALL_ROOT / name)

    lang_src = source / "lang"
    if lang_src.exists():
        lang_dst = INSTALL_ROOT / "lang"
        if lang_dst.exists():
            shutil.rmtree(lang_dst)
        shutil.copytree(lang_src, lang_dst)

    app_src = source / "app"
    for name in ("launcher.pyw", "updater.py", "uninstall.py"):
        src = app_src / name
        if src.exists():
            shutil.copy2(src, APP_DIR / name)


def create_venv(python: str) -> Path:
    if not (VENV_DIR / "Scripts" / "python.exe").exists():
        run([python, "-m", "venv", str(VENV_DIR)])
    return VENV_DIR / "Scripts" / "python.exe"


def install_python_dependencies(venv_python: Path) -> None:
    requirements = INSTALL_ROOT / "requirements.txt"
    run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], check=False)
    if requirements.exists():
        run([str(venv_python), "-m", "pip", "install", "--upgrade", "-r", str(requirements)])


def install_ffmpeg_if_missing() -> None:
    if command_exists("ffmpeg"):
        return
    if not command_exists("winget"):
        messagebox.showwarning("FFmpeg", "No se encontro FFmpeg ni winget. La app abrira, pero algunas descargas pueden fallar.")
        return
    if messagebox.askyesno("FFmpeg", "No se encontro FFmpeg. Queres instalarlo con winget?"):
        run(["winget", "install", "--id", "Gyan.FFmpeg", "-e", "--accept-package-agreements", "--accept-source-agreements"], check=False)


def latest_commit() -> str:
    try:
        request = urllib.request.Request(
            f"https://api.github.com/repos/{REPOSITORY}/commits/{BRANCH}",
            headers={"User-Agent": "YouTubeDownloaderInstaller"},
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data.get("sha", "")
    except Exception:
        return ""


def write_launcher_files(venv_python: Path) -> Path:
    pythonw = venv_python.with_name("pythonw.exe")
    python_exe = pythonw if pythonw.exists() else venv_python
    vbs_path = INSTALL_ROOT / "YouTube Downloader.vbs"
    vbs_path.write_text(
        f'Set WshShell = CreateObject("WScript.Shell")\n'
        f'WshShell.Run """" & "{python_exe}" & """" & " " & """" & "{APP_DIR / "launcher.pyw"}" & """", 0, False\n',
        encoding="utf-8",
    )
    return vbs_path


def powershell_escape(value: str) -> str:
    return value.replace("'", "''")


def create_shortcut(target: Path, shortcut: Path, working_dir: Path) -> None:
    shortcut.parent.mkdir(parents=True, exist_ok=True)
    script = (
        "$shell = New-Object -ComObject WScript.Shell\n"
        f"$shortcut = $shell.CreateShortcut('{powershell_escape(str(shortcut))}')\n"
        f"$shortcut.TargetPath = '{powershell_escape(str(target))}'\n"
        f"$shortcut.WorkingDirectory = '{powershell_escape(str(working_dir))}'\n"
        f"$shortcut.IconLocation = '{powershell_escape(str(target))}'\n"
        "$shortcut.Save()\n"
    )
    run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], check=False)


def desktop_dir() -> Path:
    return Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"


def start_menu_dir() -> Path:
    return Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"


def register_uninstaller(venv_python: Path) -> None:
    if os.name != "nt":
        return
    pythonw = venv_python.with_name("pythonw.exe")
    python_exe = pythonw if pythonw.exists() else venv_python
    uninstall_command = f'"{python_exe}" "{APP_DIR / "uninstall.py"}"'
    key = r"HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\YouTubeDownloader"
    values = [
        ("DisplayName", APP_NAME),
        ("DisplayVersion", "1.0.0"),
        ("Publisher", PUBLISHER),
        ("InstallLocation", str(INSTALL_ROOT)),
        ("UninstallString", uninstall_command),
        ("QuietUninstallString", uninstall_command),
    ]
    run(["reg", "add", key, "/f"], check=False)
    for name, value in values:
        run(["reg", "add", key, "/v", name, "/t", "REG_SZ", "/d", value, "/f"], check=False)


def write_metadata(desktop_shortcut: Path, start_shortcut: Path) -> None:
    metadata = {
        "app_name": APP_NAME,
        "repository": REPOSITORY,
        "branch": BRANCH,
        "commit": latest_commit(),
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "install_root": str(INSTALL_ROOT),
        "desktop_shortcut": str(desktop_shortcut),
        "start_menu_shortcut": str(start_shortcut),
    }
    APP_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_FILE.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def install() -> None:
    python = install_python_if_missing()
    copy_payload()
    venv_python = create_venv(python)
    install_python_dependencies(venv_python)
    install_ffmpeg_if_missing()

    launcher = write_launcher_files(venv_python)
    desktop_shortcut = desktop_dir() / "YouTube Downloader.lnk"
    start_shortcut = start_menu_dir() / "YouTube Downloader.lnk"
    create_shortcut(launcher, desktop_shortcut, INSTALL_ROOT)
    create_shortcut(launcher, start_shortcut, INSTALL_ROOT)
    register_uninstaller(venv_python)
    write_metadata(desktop_shortcut, start_shortcut)


def main() -> int:
    root = tk.Tk()
    root.withdraw()

    try:
        if not messagebox.askyesno(APP_NAME, f"Instalar {APP_NAME} en AppData?"):
            return 0
        install()
    except Exception as exc:
        messagebox.showerror(APP_NAME, f"No se pudo instalar: {exc}")
        return 1

    if messagebox.askyesno(APP_NAME, "Instalacion completa. Queres abrir la app ahora?"):
        launcher = INSTALL_ROOT / "YouTube Downloader.vbs"
        os.startfile(str(launcher))  # type: ignore[attr-defined]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
