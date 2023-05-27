@echo off
set "source=%~dp0FFmpeg"
set "destination=C:\FFmpeg"

REM Copiar la carpeta FFmpeg
xcopy "%source%" "%destination%" /E /I /Y
