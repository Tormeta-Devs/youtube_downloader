from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from tkinter import messagebox
import tkinter as tk


DEFAULT_REPOSITORY = "Tormeta-Devs/youtube_downloader"
DEFAULT_BRANCH = "main"
INSTALL_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = INSTALL_ROOT / "app"
METADATA_FILE = APP_DIR / "install.json"
UPDATE_PATHS = ("youtube_downloader.py", "requirements.txt", "README.md", "lang", "app")
SKIP_APP_FILES = {"install.json"}


def load_metadata() -> dict:
    if not METADATA_FILE.exists():
        return {}
    try:
        return json.loads(METADATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_metadata(metadata: dict) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    metadata["last_update_check"] = datetime.now(timezone.utc).isoformat()
    METADATA_FILE.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def request_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "YouTubeDownloaderUpdater"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def remote_commit(repository: str, branch: str) -> str:
    data = request_json(f"https://api.github.com/repos/{repository}/commits/{branch}")
    return data.get("sha", "")


def download_repository(repository: str, branch: str, destination: Path) -> Path:
    url = f"https://github.com/{repository}/archive/refs/heads/{branch}.zip"
    zip_path = destination / "source.zip"
    request = urllib.request.Request(url, headers={"User-Agent": "YouTubeDownloaderUpdater"})
    with urllib.request.urlopen(request, timeout=60) as response:
        zip_path.write_bytes(response.read())

    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(destination)

    roots = [path for path in destination.iterdir() if path.is_dir()]
    if not roots:
        raise RuntimeError("No se pudo extraer el repositorio.")
    return roots[0]


def copy_update(source_root: Path) -> None:
    for relative in UPDATE_PATHS:
        source = source_root / relative
        target = INSTALL_ROOT / relative
        if not source.exists():
            continue

        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            for item in source.iterdir():
                if relative == "app" and item.name in SKIP_APP_FILES:
                    continue
                destination = target / item.name
                if item.is_dir():
                    if destination.exists():
                        shutil.rmtree(destination)
                    shutil.copytree(item, destination)
                else:
                    shutil.copy2(item, destination)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def install_dependencies() -> None:
    requirements = INSTALL_ROOT / "requirements.txt"
    if not requirements.exists():
        return

    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "-r", str(requirements)],
        cwd=str(INSTALL_ROOT),
        check=False,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )


def check_and_update(interactive: bool = False) -> tuple[bool, str]:
    metadata = load_metadata()
    repository = metadata.get("repository", DEFAULT_REPOSITORY)
    branch = metadata.get("branch", DEFAULT_BRANCH)
    current = metadata.get("commit", "")

    latest = remote_commit(repository, branch)
    if not latest:
        return False, "No se pudo comprobar la version remota."

    metadata["repository"] = repository
    metadata["branch"] = branch

    if latest == current:
        metadata["commit"] = current or latest
        save_metadata(metadata)
        return False, "La app ya esta actualizada."

    if interactive and current:
        if not messagebox.askyesno("Actualizacion disponible", "Hay una nueva version. Queres instalarla ahora?"):
            metadata["commit"] = current
            save_metadata(metadata)
            return False, "Actualizacion cancelada."

    with tempfile.TemporaryDirectory(prefix="youtube_downloader_update_") as temp_dir:
        source_root = download_repository(repository, branch, Path(temp_dir))
        backup_dir = INSTALL_ROOT / "_update_backup"
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        backup_dir.mkdir(parents=True, exist_ok=True)
        for relative in UPDATE_PATHS:
            current_path = INSTALL_ROOT / relative
            if current_path.exists():
                destination = backup_dir / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                if current_path.is_dir():
                    shutil.copytree(current_path, destination)
                else:
                    shutil.copy2(current_path, destination)

        copy_update(source_root)
        install_dependencies()

    metadata["commit"] = latest
    metadata["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_metadata(metadata)
    return True, "Actualizacion instalada. Reinicia la app si ya estaba abierta."


def show_message(title: str, message: str) -> None:
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title, message)
    root.destroy()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--startup", action="store_true")
    parser.add_argument("--gui", action="store_true")
    args = parser.parse_args()

    if not METADATA_FILE.exists():
        if args.gui:
            show_message("Actualizaciones", "Esta copia no parece estar instalada en AppData.")
        return 0

    try:
        updated, message = check_and_update(interactive=args.gui)
    except Exception as exc:
        if args.gui:
            show_message("Actualizaciones", f"No se pudo actualizar: {exc}")
        return 1

    if args.gui:
        show_message("Actualizaciones", message)
    return 0 if not updated else 2


if __name__ == "__main__":
    raise SystemExit(main())
