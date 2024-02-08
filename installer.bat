@echo off
rem Comprobar si Python está instalado
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python está instalado.
) else (
    echo Python no está instalado.
    rem Instalar winget si no está instalado (la siguiente linea de codigo hecho por IA)
    powershell -Command "if (-not (Get-AppxPackage Microsoft.DesktopAppInstaller)) {Add-AppxPackage -Path 'C:\Program Files\WindowsApps\Microsoft.DesktopAppInstaller_1.16.12653.0_x64__8wekyb3d8bbwe\AppInstaller_1.16.12653.0_x64.appxbundle'}"
    rem Instalar Python desde winget
    winget install -e --id Python.Python.3.12 --scope machine
    rem Actualizar la variable de entorno PATH
    setx /M path "%path%;C:\Program Files\Python312"
    echo Python se ha instalado correctamente.
)
rem Comprobar si FFmpeg está instalado
ffmpeg -version >nul 2>&1
if %errorlevel% equ 0 (
    echo FFmpeg está instalado.
) else (
    echo FFmpeg no está instalado.
    rem Instalar FFmpeg desde winget
    winget install FFmpeg
    echo FFmpeg se ha instalado correctamente.
)
rem
python.exe -m pip install --upgrade pip
python.exe -m pip install -r requeriments.txt
pause
