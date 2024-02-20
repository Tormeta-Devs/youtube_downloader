import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox
from xml.etree import ElementTree as ET
from youtubesearchpython import Search
import webbrowser
import threading

# Variables globales
output_directory = os.path.join(os.path.expanduser("~"), "Downloads")
download_counter = 0
default_format = "mp3"
messages = {}  # Variable global para almacenar mensajes
languages = ["es", "en"]  # Ejemplo de idiomas disponibles
default_language = "es"  # Idioma por defecto
language_index = 0  # Índice del idioma en el menú
video_ids = []

def load_messages(language):
    global messages
    messages_path = os.path.join("lang", f"messages_{language}.xml")
    if not os.path.exists(messages_path):
        print(f"Error: No se encontró el archivo de mensajes para el idioma {language}")
        return {}
    
    try:
        tree = ET.parse(messages_path)
        root = tree.getroot()
        messages = {subchild.tag: subchild.text for child in root for subchild in child}
    except Exception as e:
        print(f"Error al cargar mensajes desde {messages_path}: {e}")
    
    return messages

def change_language(language):
    global messages, language_index
    messages = load_messages(language)
    language_index = languages.index(language)
    language_menu.entryconfig(language_index, label=messages.get('language_name', language.capitalize()))
    window.title(messages.get('window_title', 'YouTube-Downloader'))

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
    selected_index = result_listbox.curselection()
    if selected_index:
        selected_id = video_ids[selected_index[0]]
        video_url = f"https://www.youtube.com/watch?v={selected_id}"
        selected_format = format_combobox.get() or default_format
        download_command = f"youtube-dl -o \"{output_directory}/%(title)s.%(ext)s\" -x --audio-format {selected_format} {video_url}" if selected_format != "webm" else f"youtube-dl -o \"{output_directory}/%(title)s.%(ext)s\" -f bestvideo {video_url}"
        threading.Thread(target=perform_download, args=(download_command,)).start()
        download_counter += 1
        update_title()
    else:
        messagebox.showerror(messages.get("select_video", "Error"), messages.get("select_video_message", "Por favor, selecciona un video de la lista."))

def select_directory():
    global output_directory
    output_directory = filedialog.askdirectory()
    directory_label.config(text=output_directory)

def perform_download(download_command):
    subprocess.Popen(download_command, shell=True).wait()

def update_title():
    window.title(f"{messages.get('window_title', 'YouTube-Downloader')} | FFmpeg: {get_ffmpeg_version()} | Descargas: {download_counter}")

def get_ffmpeg_version():
    try:
        version_output = subprocess.check_output(["ffmpeg", "-version"]).decode("utf-8")
        version_line = version_output.splitlines()[0]
        version = version_line.split("version ")[1].split(" ")[0]
        return version
    except Exception as e:
        print(f"Error al obtener la versión de FFmpeg: {e}")
        return "Desconocida"

# Crear ventana
window = tk.Tk()
window.title("YouTube-Downloader")
window.geometry("500x400")
window.resizable(False, False)

# Menú de idioma
language_menu = tk.Menu(window)
for lang in languages:
    language_menu.add_command(label=lang.capitalize(), command=lambda l=lang: change_language(l))
window.config(menu=language_menu)

# Campo de entrada para la búsqueda de YouTube
entry = tk.Entry(window)
entry.pack()

# Botón para iniciar la búsqueda
search_button = tk.Button(window, text="Buscar en YouTube", command=search_youtube)
search_button.pack()

# Lista de resultados
result_listbox = tk.Listbox(window)
result_listbox.pack()

# Selector de formatos
format_combobox = Combobox(window, values=["aac", "flac", "mp3", "m4a", "opus", "vorbis", "wav", "webm"], state="readonly")
format_combobox.current(format_combobox["values"].index(default_format))  # Establecer formato por defecto
format_combobox.pack()

# Etiqueta para mostrar el directorio seleccionado
directory_label = tk.Label(window, text=output_directory)
directory_label.pack()

# Botón para seleccionar directorio
directory_button = tk.Button(window, text="Seleccionar directorio", command=select_directory)
directory_button.pack()

# Botón de descarga
download_button = tk.Button(window, text="Descargar", command=download_audio_or_video)
download_button.pack()

# Ejecutar ventana
window.mainloop()