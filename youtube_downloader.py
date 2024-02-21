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

# Ruta del archivo de configuración
config_file = "config.txt"

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

def save_language(language):
    with open(config_file, "w") as f:
        f.write(language)

def load_language():
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            return f.read().strip()
    else:
        return default_language

def change_language(language):
    global messages, language_index
    messages = load_messages(language)
    language_index = languages.index(language)
    save_language(language)
    window.title(messages.get('window_title', 'YouTube-Downloader') + f" | FFmpeg: {get_ffmpeg_version()}" + f" | Descargas: {download_counter}")
    update_button_texts()
    update_language_menu()

def check_ffmpeg_update():
    subprocess.Popen(["winget", "upgrade", "ffmpeg"]).wait()
    messagebox.showinfo(messages.get('ffmpeg_update_title', 'FFmpeg Update'), messages.get('ffmpeg_update_message', 'FFmpeg ha sido actualizado.'))

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

def update_button_texts():
    search_button.config(text=messages.get('search_button', 'Buscar en YouTube'))
    directory_button.config(text=messages.get('directory_button', 'Cambiar Directorio'))
    download_button.config(text=messages.get('download_button', 'Descargar'))
    play_button.config(text=messages.get('play_button', 'Escuchar'))
    update_language_menu()

def update_language_menu():
    global language_menu
    language_menu.delete(0, tk.END)  # Limpiar el menú existente
    for lang in languages:
        language_menu.add_command(label=messages.get(f'language_name_{lang}', lang.capitalize()), command=lambda l=lang: change_language(l))

# Crear ventana
window = tk.Tk()
window.title("YouTube-Downloader")
window.geometry("800x600")  # Aumentando el tamaño de la ventana
window.resizable(True, True)  # Permitiendo que la ventana sea redimensionable

# Menú de idioma
language_menu = tk.Menu(window)
update_language_menu()
window.config(menu=language_menu)

# Sección de ajustes
settings_menu = tk.Menu(window)
language_submenu = tk.Menu(settings_menu, tearoff=0)
settings_menu.add_cascade(label="Languages", menu=language_submenu)
language_submenu.add_command(label="Spanish", command=lambda: change_language('es'))
language_submenu.add_command(label="English", command=lambda: change_language('en'))
settings_menu.add_command(label="Check Updates", command=check_ffmpeg_update)
window.config(menu=settings_menu)

# Contenedor para botones y widgets relacionados
button_frame = tk.Frame(window)
button_frame.pack(pady=10)

# Campo de entrada para la búsqueda de YouTube
entry = tk.Entry(button_frame)
entry.grid(row=0, column=0, padx=10)

# Botón para buscar en YouTube
search_button = tk.Button(button_frame)
search_button.grid(row=0, column=1, padx=10)

# Botón para iniciar la descarga
download_button = tk.Button(button_frame)
download_button.grid(row=0, column=2, padx=10)

# Botón para escuchar
play_button = tk.Button(button_frame)
play_button.grid(row=0, column=3, padx=10)

# Menú desplegable para seleccionar el formato de descarga
format_combobox = Combobox(button_frame, values=["mp3", "m4a", "opus", "vorbis", "wav", "webm"])
format_combobox.grid(row=0, column=4, padx=10)

# Botón para seleccionar directorio
directory_button = tk.Button(window)
directory_button.pack(side=tk.LEFT, padx=10)

# Etiqueta para el directorio seleccionado
directory_label = tk.Label(window, text=output_directory)
directory_label.pack(side=tk.LEFT, padx=10)

# Lista de resultados de búsqueda
result_listbox = tk.Listbox(window)
result_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

# Cargar los mensajes en el idioma predeterminado
last_language = load_language()
print("Idioma cargado:", last_language)
change_language(last_language)
print("Idioma después de cambio:", last_language)

# Ejecutar ventana
window.mainloop()