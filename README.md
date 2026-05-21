[![Buy Me a Coffee](https://www.codehim.com/wp-content/uploads/2022/09/bmc-button.png)](https://www.buymeacoffee.com/juanegameryt)

# YouTube-Downloader

## Espanol

> Hola, somos Tormenta-Devs. Este proyecto busca simplificar la descarga de musica y videos de YouTube desde una app de escritorio clara, rapida y facil de usar.

## De que trata?

YouTube-Downloader es una aplicacion hecha con Python y Tkinter que permite buscar videos de YouTube, previsualizar el audio sin descargarlo, elegir el formato deseado y guardar el resultado en la carpeta que prefieras.

La idea es evitar procesos largos o paginas poco confiables: buscas, seleccionas, eliges formato y descargas.

## Funciones principales

- Busqueda directa en YouTube usando `yt-dlp` o `youtube-dl`.
- Resultados en tabla con titulo, canal, duracion, vistas y miniatura.
- Vista previa de audio sin guardar el archivo localmente.
- Boton para abrir el resultado seleccionado en YouTube.
- Boton para copiar la URL del video.
- Selector de carpeta y boton para abrir la carpeta de descargas.
- Descarga de audio en `mp3`, `m4a`, `aac`, `flac`, `opus`, `vorbis` y `wav`.
- Descarga de video en `mp4` o `webm`.
- Barra de progreso, registro de actividad y boton para detener operaciones.
- Modo claro y modo oscuro, guardados automaticamente en la configuracion.
- Panel de seleccion actual para revisar rapido el video elegido.
- Interfaz bilingue: espanol e ingles.
- Deteccion de `FFmpeg` y del motor de descarga disponible.
- Instalacion automatica opcional de `yt-dlp` y `Pillow` si faltan.

## Requisitos

- Python 3.10 o superior.
- `yt-dlp`, recomendado para buscar y descargar.
- `Pillow`, necesario para mostrar miniaturas.
- `FFmpeg`, necesario para convertir audio y combinar video/audio.

Puedes instalar las librerias de Python con:

```bash
pip install -r requirements.txt
```

En Windows, tambien puedes instalar las herramientas principales con `winget`:

```powershell
winget install --id yt-dlp.yt-dlp -e
winget install --id Gyan.FFmpeg -e
```

## Como utilizarlo

1. Descarga la release mas reciente o clona el repositorio.
2. Instala los requisitos.
3. Abre una terminal en la carpeta del proyecto.
4. Ejecuta:

```bash
python youtube_downloader.py
```

Si `python` no funciona en Windows, prueba:

```powershell
py youtube_downloader.py
```

Una vez abierta la app:

- Escribe el nombre de una cancion o video.
- Presiona `Buscar`.
- Selecciona un resultado.
- Usa `Vista previa` si quieres escucharlo sin descargar.
- Usa `YouTube` si quieres abrirlo en el navegador.
- Elige formato y carpeta.
- Presiona `Descargar`.

El tiempo de busqueda y descarga depende de tu conexion, tu equipo y la respuesta de YouTube.

---

# YouTube-Downloader

## English

> Hello, we are Tormenta-Devs. This project is designed to simplify downloading music and videos from YouTube through a clean, fast, and easy-to-use desktop app.

## What is it about?

YouTube-Downloader is a Python and Tkinter desktop application that lets you search YouTube videos, preview audio without downloading it, choose an output format, and save the result to your preferred folder.

The goal is to avoid long workflows or unreliable websites: search, select, choose a format, and download.

## Main Features

- Direct YouTube search using `yt-dlp` or `youtube-dl`.
- Results table with title, channel, duration, views, and thumbnail.
- Audio preview without saving the file locally.
- Button to open the selected result on YouTube.
- Button to copy the video URL.
- Folder selector and button to open the download folder.
- Audio download in `mp3`, `m4a`, `aac`, `flac`, `opus`, `vorbis`, and `wav`.
- Video download in `mp4` or `webm`.
- Progress bar, activity log, and stop button.
- Light mode and dark mode, saved automatically in the configuration.
- Current selection panel to quickly review the selected video.
- Bilingual interface: Spanish and English.
- Detection of `FFmpeg` and the available download engine.
- Optional automatic installation of `yt-dlp` and `Pillow` if missing.

## Requirements

- Python 3.10 or higher.
- `yt-dlp`, recommended for searching and downloading.
- `Pillow`, required for thumbnails.
- `FFmpeg`, required for audio conversion and video/audio merging.

Install Python dependencies with:

```bash
pip install -r requirements.txt
```

On Windows, you can also install the main tools with `winget`:

```powershell
winget install --id yt-dlp.yt-dlp -e
winget install --id Gyan.FFmpeg -e
```

## How To Use

1. Download the latest release or clone the repository.
2. Install the requirements.
3. Open a terminal inside the project folder.
4. Run:

```bash
python youtube_downloader.py
```

If `python` does not work on Windows, try:

```powershell
py youtube_downloader.py
```

Once the app opens:

- Type the name of a song or video.
- Press `Search`.
- Select a result.
- Use `Preview` if you want to listen without downloading.
- Use `YouTube` if you want to open it in the browser.
- Choose format and folder.
- Press `Download`.

Search and download time depends on your connection, your computer, and YouTube's response.
