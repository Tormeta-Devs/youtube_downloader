# -*- coding: utf-8 -*-
"""
Este script realiza la descarga de audio o video desde YouTube.

Copyright (c) 2024 Juan Mellano (Fundador de Tormenta-Devs)

Se concede permiso, de forma gratuita, a cualquier persona que obtenga una copia
de este software y los archivos de documentación asociados (el "Software"), para
tratar el Software sin restricciones, incluyendo, sin limitación, los derechos
para usar, copiar, modificar, fusionar, publicar, distribuir, sublicenciar y/o vender
copias del Software, y para permitir a las personas a las que se les proporcione el
Software a hacerlo, con sujeción a las siguientes condiciones:

El aviso de copyright anterior y este aviso de permiso se incluirán en todas las copias
o porciones sustanciales del Software.

EL SOFTWARE SE PROPORCIONA "TAL CUAL", SIN GARANTÍA DE NINGÚN TIPO, EXPRESA O IMPLÍCITA,
INCLUYENDO PERO NO LIMITADO A LAS GARANTÍAS DE COMERCIABILIDAD, IDONEIDAD PARA UN PROPÓSITO
PARTICULAR Y NO INFRACCIÓN. EN NINGÚN CASO LOS AUTORES O TITULARES DE LOS DERECHOS DE AUTOR
SERÁN RESPONSABLES DE NINGÚN RECLAMO, DAÑO U OTRA RESPONSABILIDAD, YA SEA EN UNA ACCIÓN DE
CONTRATO, AGRAVIO O DE OTRO MODO, DERIVADO DE, FUERA DE O EN CONEXIÓN CON EL SOFTWARE O EL USO
U OTROS TRATOS EN EL SOFTWARE.

Las copias ilegales de este software no están disponibles. Si desea realizar
personalizaciones, por favor, realice un fork del repositorio en GitHub:
https://github.com/Tormeta-Devs/youtube_downloader
"""
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox
from youtubesearchpython import Search
import subprocess
import webbrowser
import threading
import os

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
    video_ids.clear()  # Vaciar la lista de IDs de videos
    for i, result in enumerate(results, start=1):
        result_listbox.insert(tk.END, f"{i}. {result['title']}")
        video_ids.append(result['id'])

def download_audio_or_video():
    if not output_directory:
        messagebox.showerror("Error", "Antes de descargar, selecciona un directorio")
        return
    selected_index = result_listbox.curselection()
    if selected_index:
        selected_id = video_ids[selected_index[0]]
        video_url = f"https://www.youtube.com/watch?v={selected_id}"
        selected_format = format_combobox.get()
        if selected_format == "webm":
            download_command = f"youtube-dl -o \"{output_directory}/%(title)s.%(ext)s\" -f bestvideo {video_url}"
        else:
            download_command = f"youtube-dl -o \"{output_directory}/%(title)s.%(ext)s\" -x --audio-format {selected_format} {video_url}"
        disable_ui()
        threading.Thread(target=perform_download, args=(download_command,)).start()

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

window = tk.Tk()
window.title("Descargar audio o video de YouTube")

# Ajustar el tamaño de la ventana
window_width = 500
window_height = 300
window.geometry(f"{window_width}x{window_height}")
window.resizable(False, False)

entry = tk.Entry(window, width=40)
entry.pack(pady=10)
entry.bind("<Return>", on_enter_key_pressed)

search_button = tk.Button(window, text="Buscar en YouTube", command=search_youtube)
search_button.pack()

result_listbox = tk.Listbox(window, width=50)
result_listbox.pack(pady=10)

button_frame = tk.Frame(window)
button_frame.pack()

directory_button = tk.Button(button_frame, text="Seleccionar directorio", command=select_directory)
directory_button.grid(row=0, column=0)

download_button = tk.Button(button_frame, text="Descargar", command=download_audio_or_video, state=tk.DISABLED)
download_button.grid(row=0, column=1, padx=5)

format_combobox = Combobox(button_frame, values=["mp3", "aac", "flac", "webm", "m4a", "opus", "vorbis", "wav"], state="readonly")
format_combobox.current(0)  # Establecer el valor predeterminado
format_combobox.grid(row=0, column=2, padx=5)

play_button = tk.Button(button_frame, text="Escuchar", command=play_video)
play_button.grid(row=0, column=3, padx=5)

directory_label = tk.Label(window, text="Directorio de salida:")
directory_label.pack()

video_ids = []

window.mainloop()