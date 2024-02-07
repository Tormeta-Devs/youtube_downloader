@echo off
rem Comprobar si Python está instalado
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python esta instalado.
) else (
    echo Python no esta instalado.
    rem Instalar winget si no está instalado
    powershell -Command "if (-not (Get-AppxPackage Microsoft.DesktopAppInstaller)) {Add-AppxPackage -Path 'C:\Program Files\WindowsApps\Microsoft.DesktopAppInstaller_1.16.12653.0_x64__8wekyb3d8bbwe\AppInstaller_1.16.12653.0_x64.appxbundle'}"
    rem Instalar Python desde winget
    winget install -e --id Python.Python.3.12 --scope machine
    rem Actualizar la variable de entorno PATH
    setx /M path "%path%;C:\Program Files\Python312"
    echo Python se ha instalado correctamente.
)
rem Ejecutar el código que me has dado
python.exe -m pip install -r requeriments.txt
pause
