# -*- coding: cp1252 -*-
import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar
from youtubesearchpython import Search
import subprocess
import webbrowser
import re

def select_directory():
    global output_directory
    output_directory = filedialog.askdirectory()
    directory_label.config(text=output_directory)

def search_youtube():
    search_query = entry.get()
    allSearch = Search(search_query, limit=10)
    results = allSearch.result()['result']
    result_listbox.delete(0, tk.END)
    video_ids.clear()  # Vaciar la lista de IDs de videos
    for i, result in enumerate(results, start=1):
        result_listbox.insert(tk.END, f"{i}. {result['title']}")
        video_ids.append(result['id'])

def download_audio():
    selected_index = result_listbox.curselection()
    if selected_index:
        selected_id = video_ids[selected_index[0]]
        video_url = f"https://www.youtube.com/watch?v={selected_id}"
        download_command = f"youtube-dl --ffmpeg-location C://FFmpeg//bin -o {output_directory}%(title)s.%(ext)s --extract-audio --audio-format mp3 {video_url}"
        subprocess.Popen(download_command, shell=True)

def play_video():
    selected_index = result_listbox.curselection()
    if selected_index:
        selected_id = video_ids[selected_index[0]]
        video_url = f"https://www.youtube.com/watch?v={selected_id}"
        webbrowser.open(video_url)

window = tk.Tk()
window.title("Descargar audio de YouTube")

# Ajustar el tama�o de la ventana
window_width = 600
window_height = 300
window.geometry(f"{window_width}x{window_height}")

entry = tk.Entry(window, width=40)
entry.pack(pady=10)

search_button = tk.Button(window, text="Buscar en YouTube", command=search_youtube)
search_button.pack()

result_listbox = tk.Listbox(window, width=50)
result_listbox.pack(pady=10)

button_frame = tk.Frame(window)
button_frame.pack()

directory_button = tk.Button(button_frame, text="Seleccionar directorio", command=select_directory)
directory_button.pack(side=tk.LEFT)

download_button = tk.Button(button_frame, text="Descargar", command=download_audio)
download_button.pack(side=tk.LEFT, padx=10)

play_button = tk.Button(button_frame, text="Escuchar", command=play_video)
play_button.pack(side=tk.LEFT)

directory_label = tk.Label(window, text="Directorio de salida:")
directory_label.pack()

progress_bar = Progressbar(window, mode="determinate", maximum=100)
progress_bar.pack(pady=10)

video_ids = []

window.mainloop()
