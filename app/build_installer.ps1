$ErrorActionPreference = "Stop"

$AppDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $AppDir
Set-Location $AppDir

function Find-Python {
    $commands = @("py", "python")
    foreach ($command in $commands) {
        $found = Get-Command $command -ErrorAction SilentlyContinue
        if ($found) {
            return $command
        }
    }
    throw "Python no esta disponible en PATH. Instala Python 3 antes de generar el instalador."
}

$Python = Find-Python

& $Python -m pip install --upgrade pip pyinstaller

& $Python -m PyInstaller `
    --noconfirm `
    --onefile `
    --windowed `
    --name "YouTubeDownloaderInstaller" `
    --add-data "$RootDir\youtube_downloader.py;payload" `
    --add-data "$RootDir\requirements.txt;payload" `
    --add-data "$RootDir\README.md;payload" `
    --add-data "$RootDir\lang;payload\lang" `
    --add-data "$AppDir\launcher.pyw;payload\app" `
    --add-data "$AppDir\updater.py;payload\app" `
    --add-data "$AppDir\uninstall.py;payload\app" `
    "$AppDir\installer.py"

Write-Host ""
Write-Host "Instalador generado en:"
Write-Host "$AppDir\dist\YouTubeDownloaderInstaller.exe"
