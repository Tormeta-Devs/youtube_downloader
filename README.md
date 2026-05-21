# YouTube Downloader

Aplicacion de escritorio hecha con Python y Tkinter para buscar videos de YouTube y descargarlos como audio o video.

## Funciones

- Busqueda directa en YouTube usando `yt-dlp` o `youtube-dl`.
- Resultados en tabla con titulo, canal, duracion y vistas.
- Miniaturas de cada resultado cuando `Pillow` esta instalado.
- Descarga de audio en `mp3`, `m4a`, `aac`, `flac`, `opus`, `vorbis` y `wav`.
- Descarga de video en `mp4` o `webm`.
- Selector de carpeta, boton para abrir carpeta, copiar URL y abrir el video en YouTube.
- Barra de progreso, registro de actividad y boton para detener operaciones.
- Interfaz bilingue: espanol e ingles.
- Deteccion de `FFmpeg` y del motor de descarga disponible.

## Requisitos

- Python 3.10 o superior.
- `yt-dlp` recomendado:

```bash
pip install -r requirements.txt
```

- `FFmpeg` para convertir audio y combinar video/audio.

En Windows tambien podes instalar herramientas con `winget`:

```powershell
winget install --id yt-dlp.yt-dlp -e
winget install --id Gyan.FFmpeg -e
```

## Uso

```bash
python youtube_downloader.py
```

Luego busca un video, selecciona un resultado, elige formato y carpeta, y presiona `Descargar`.
