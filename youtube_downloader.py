# -*- coding: cp1252 -*-
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox
from youtubesearchpython import Search
import subprocess
import webbrowser
import re

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
    video_ids.clear()  # Reinciar la busqueda
    for i, result in enumerate(results, start=1):
        result_listbox.insert(tk.END, f"{i}. {result['title']}")
        video_ids.append(result['id'])

def download_audio_or_video():
    selected_index = result_listbox.curselection()
    if selected_index:
        selected_id = video_ids[selected_index[0]]
        video_url = f"https://www.youtube.com/watch?v={selected_id}"
        selected_format = format_combobox.get()
        if selected_format == "webm":
            download_command = f"youtube-dl -o {output_directory}/%(title)s.%(ext)s -f bestvideo {video_url}"
        else:
            download_command = f"youtube-dl -o {output_directory}//%(title)s.%(ext)s -x --audio-format {selected_format} {video_url}"
        subprocess.Popen(download_command, shell=True)

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

def update_format_button_state(event=None):
    if format_combobox.get():
        download_button.config(state=tk.NORMAL)
    else:
        download_button.config(state=tk.DISABLED)

def on_enter_key_pressed(event):
    search_youtube()

def show_format_warning():
    messagebox.showwarning("Advertencia", "Debes seleccionar un formato")

def show_directory_warning():
    messagebox.showwarning("Advertencia", "Antes de descargar, selecciona un directorio")

window = tk.Tk()
window.title("Descargar audio o video de YouTube")

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

format_combobox = Combobox(button_frame, values=["webm", "aac", "flac", "mp3", "m4a", "opus", "vorbis", "wav"], state="readonly")
format_combobox.current(0)  # Establecer el valor predeterminado
format_combobox.grid(row=0, column=2, padx=5)
format_combobox.bind("<<ComboboxSelected>>", update_format_button_state)

play_button = tk.Button(button_frame, text="Escuchar", command=play_video)
play_button.grid(row=0, column=3, padx=5)

directory_label = tk.Label(window, text="Directorio de salida:")
directory_label.pack()

video_ids = []

window.mainloop()