import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox
from youtubesearchpython import Search
import webbrowser
import threading

# Variables globales
output_directory = ""
download_counter = 0

def select_directory():
    global output_directory
    output_directory = filedialog.askdirectory()
    directory_label.config(text=output_directory)
    update_download_button_state()

def search_youtube(*args):
    search_query = entry.get()
    allSearch = Search(search_query, limit=10)
    results = allSearch.result()['result']
    result_listbox.delete(0, tk.END)
    video_ids.clear()
    for i, result in enumerate(results, start=1):
        result_listbox.insert(tk.END, f"{i}. {result['title']}")
        video_ids.append(result['id'])

def download_audio_or_video():
    global download_counter
    if not output_directory:
        messagebox.showerror("Error", "Antes de descargar, selecciona un directorio")
        return
    selected_index = result_listbox.curselection()
    if selected_index:
        selected_id = video_ids[selected_index[0]]
        video_url = f"https://www.youtube.com/watch?v={selected_id}"
        selected_format = format_combobox.get()
        download_command = f"youtube-dl -o \"{output_directory}/%(title)s.%(ext)s\" -x --audio-format {selected_format} {video_url}" if selected_format != "webm" else f"youtube-dl -o \"{output_directory}/%(title)s.%(ext)s\" -f bestvideo {video_url}"
        disable_ui()
        threading.Thread(target=perform_download, args=(download_command,)).start()
        download_counter += 1
        update_title()

def perform_download(download_command):
    subprocess.Popen(download_command, shell=True).wait()
    enable_ui()

def play_video():
    selected_index = result_listbox.curselection()
    if selected_index:
        selected_id = video_ids[selected_index[0]]
        video_url = f"https://www.youtube.com/watch?v={selected_id}"
        webbrowser.open(video_url)

def update_download_button_state():
    if output_directory:
        download_button.config(state=tk.NORMAL)
    else:
        download_button.config(state=tk.DISABLED)

def on_enter_key_pressed(event):
    search_youtube()

def disable_ui():
    for widget in (entry, search_button, result_listbox, directory_button, format_combobox, play_button):
        widget.config(state=tk.DISABLED)
    window.config(cursor="wait")

def enable_ui():
    for widget in (entry, search_button, result_listbox, directory_button, format_combobox, play_button):
        widget.config(state=tk.NORMAL)
    window.config(cursor="")

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        install_ffmpeg_with_winget()

def install_ffmpeg_with_winget():
    try:
        subprocess.run(["winget", "install", "ffmpeg"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        messagebox.showinfo("Info", "FFmpeg se ha instalado correctamente.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"No se pudo instalar FFmpeg: {e.stderr}")

def update_title():
    window.title(f"YouTube-Downloader | FFmpeg: {get_ffmpeg_version()} | Descargas: {download_counter}")

def get_ffmpeg_version():
    try:
        version_output = subprocess.check_output(["ffmpeg", "-version"]).decode("utf-8")
        version_line = version_output.splitlines()[0]
        version = version_line.split("version ")[1].split(" ")[0]
        return version
    except Exception as e:
        print(f"Error al obtener la versión de FFmpeg: {e}")
        return "Desconocida"

# Verificar si FFmpeg está instalado
check_ffmpeg()

# Crear ventana
window = tk.Tk()
window.title("YouTube-Downloader")
window.geometry("600x300")
window.resizable(False, False)

# Entrada de búsqueda
entry = tk.Entry(window, width=40)
entry.pack(pady=10)
entry.bind("<Return>", on_enter_key_pressed)

# Botón de búsqueda
search_button = tk.Button(window, text="Buscar en YouTube", command=search_youtube)
search_button.pack()

# Lista de resultados
result_listbox = tk.Listbox(window, width=50)
result_listbox.pack(pady=10)

# Frame para botones
button_frame = tk.Frame(window)
button_frame.pack()

# Botón para seleccionar directorio
directory_button = tk.Button(button_frame, text="Seleccionar directorio", command=select_directory)
directory_button.pack(side=tk.LEFT)

# Botón de descarga
download_button = tk.Button(button_frame, text="Descargar", command=download_audio_or_video, state=tk.DISABLED)
download_button.pack(side=tk.LEFT, padx=10)

# Selector de formatos
format_combobox = Combobox(button_frame, values=["aac", "flac", "mp3", "m4a", "opus", "vorbis", "wav", "webm"], state="readonly")
format_combobox.pack(side=tk.LEFT)

# Botón de reproducción
play_button = tk.Button(button_frame, text="Reproducir", command=play_video)
play_button.pack(side=tk.LEFT)

# Etiqueta de directorio
directory_label = tk.Label(window, text="Directorio de salida:")
directory_label.pack()

# Contador de descargas
download_counter_label = tk.Label(window, text=f"Descargas: {download_counter}")
download_counter_label.pack()

# Funciones auxiliares
video_ids = []

def update_download_button_state():
    if output_directory:
        download_button.config(state=tk.NORMAL)
    else:
        download_button.config(state=tk.DISABLED)

def update_title():
    window.title(f"YouTube-Downloader | FFmpeg: {get_ffmpeg_version()} | Descargas: {download_counter}")

def on_enter_key_pressed(event):
    search_youtube()

def disable_ui():
    for widget in (entry, search_button, result_listbox, directory_button, format_combobox, play_button):
        widget.config(state=tk.DISABLED)
    window.config(cursor="wait")

def enable_ui():
    for widget in (entry, search_button, result_listbox, directory_button, format_combobox, play_button):
        widget.config(state=tk.NORMAL)
    window.config(cursor="")

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        install_ffmpeg_with_winget()

def install_ffmpeg_with_winget():
    try:
        subprocess.run(["winget", "install", "ffmpeg"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        messagebox.showinfo("Info", "FFmpeg se ha instalado correctamente.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"No se pudo instalar FFmpeg: {e.stderr}")

def get_ffmpeg_version():
    try:
        version_output = subprocess.check_output(["ffmpeg", "-version"]).decode("utf-8")
        version_line = version_output.splitlines()[0]
        version = version_line.split("version ")[1].split(" ")[0]
        return version
    except Exception as e:
        print(f"Error al obtener la versión de FFmpeg: {e}")
        return "Desconocida"

# Verificar si FFmpeg está instalado
check_ffmpeg()

# Ejecutar ventana
window.mainloop()