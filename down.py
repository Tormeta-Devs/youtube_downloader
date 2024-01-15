# down.py
import sys
import subprocess

def descargar_video(id_video, formato, output_directory):
    video_url = f"https://www.youtube.com/watch?v={id_video}"
    ffmpeg_path = "FFmpeg/bin"
    download_command = f"youtube-dl --ffmpeg-location {ffmpeg_path} -o {output_directory}%(title)s.%(ext)s -f 'best[ext={formato}]' {video_url}"

    try:
        # Ejecutar el comando de descarga
        subprocess.run(download_command, shell=True, check=True)
        print("Descarga exitosa.")
    except subprocess.CalledProcessError as e:
        print(f"Error en la descarga: {e}")

if __name__ == "__main__":
    # Obtener argumentos de la línea de comandos
    id_video = sys.argv[1]
    formato = sys.argv[2]
    output_directory = sys.argv[3]

    # Llamar a la función de descarga
    descargar_video(id_video, formato, output_directory)
