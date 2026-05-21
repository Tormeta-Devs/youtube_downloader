from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


INSTALL_ROOT = Path(__file__).resolve().parents[1]
UPDATER = INSTALL_ROOT / "app" / "updater.py"
APP_FILE = INSTALL_ROOT / "youtube_downloader.py"


def run_startup_update() -> None:
    if not UPDATER.exists():
        return

    try:
        subprocess.run(
            [sys.executable, str(UPDATER), "--startup"],
            cwd=str(INSTALL_ROOT),
            timeout=180,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    except Exception:
        pass


def main() -> None:
    os.chdir(INSTALL_ROOT)
    sys.path.insert(0, str(INSTALL_ROOT))
    run_startup_update()

    import youtube_downloader

    youtube_downloader.main()


if __name__ == "__main__":
    main()
