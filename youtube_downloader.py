import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

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

def load_language():
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            for line in f:
                if line.strip().startswith("Lang:"):
                    return line.strip().split(":")[1].strip()
    return default_language

def save_language(language):
    with open(config_file, "w") as f:
        f.write(f"Lang: {language}\n")

def load_messages(language):
    messages_path = os.path.join("lang", f"messages_{language}.xml")
    if not os.path.exists(messages_path):
        print(f"Error: No se encontró el archivo de mensajes para el idioma {language}")
        return {}
    
    try:
        tree = ET.parse(messages_path)
        root = tree.getroot()
        return {subchild.tag: subchild.text for child in root for subchild in child}
    except Exception as e:
        print(f"Error al cargar mensajes desde {messages_path}: {e}")
        return {}

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
    try:
        allSearch = Search(search_query, limit=10)
        results = allSearch.result()['result']
        result_listbox.delete(0, tk.END)
        video_ids.clear()  # Vaciar la lista de IDs de videos
        for i, result in enumerate(results, start=1):
            result_listbox.insert(tk.END, f"{i}. {result['title']}")
            video_ids.append(result['id'])
    except Exception as e:
        messagebox.showerror("Error", f"Error durante la búsqueda: {e}")

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
        download_button.config(state=tk.DISABLED, cursor="wait")  # Deshabilitar botón y cambiar cursor
        window.update()  # Actualizar ventana
    else:
        messagebox.showerror(messages.get("select_video", "Error"), messages.get("select_video_message", "Por favor, selecciona un video de la lista."))

def select_directory():
    global output_directory
    output_directory = filedialog.askdirectory()
    directory_label.config(text=output_directory)

def perform_download(download_command):
    subprocess.Popen(download_command, shell=True).wait()
    download_button.config(state=tk.NORMAL, cursor="")  # Habilitar botón y restaurar cursor
    window.update()  # Actualizar ventana

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
    search_button.config(text=messages.get('search_button', 'Buscar'), background='white', command=search_youtube)
    directory_button.config(text=messages.get('directory_button', 'Cambiar Directorio'), background='white', command=select_directory)
    download_button.config(text=messages.get('download_button', 'Descargar'), background='white', command=download_audio_or_video)
    play_button.config(text=messages.get('play_button', 'Escuchar'), background='white', command=play_audio)
    update_language_menu()

def update_language_menu():
    global language_menu
    language_menu.delete(0, tk.END)  # Limpiar el menú existente
    for lang in languages:
        language_menu.add_command(label=messages.get(f'language_name_{lang}', lang.capitalize()), command=lambda l=lang: change_language(l))

def play_audio():
    # Aquí debería ir la lógica para reproducir el audio
    pass

def on_button_press(event):
    widget = event.widget
    widget._drag_start_x = event.x
    widget._drag_start_y = event.y

def on_button_drag(event):
    widget = event.widget
    x = widget.winfo_x() - widget._drag_start_x + event.x
    y = widget.winfo_y() - widget._drag_start_y + event.y
    widget.place(x=x, y=y)

def edit_gui():
    # Deshabilitar botones durante la edición
    for widget in [search_button, play_button, download_button, directory_button, format_combobox, entry, result_listbox]:
        widget.config(state=tk.DISABLED)

    # Crear la ventana de edición
    edit_window = tk.Toplevel(window)
    edit_window.title("Edit GUI")
    edit_window.geometry("300x200")

    # Fondo blanco y texto negro
    edit_window.configure(bg="white")
    edit_window.tk_setPalette(background="white", foreground="black")

    # Botones para guardar, deshacer y rehacer cambios
    save_button = tk.Button(edit_window, text="Guardar", command=save_gui_state)
    save_button.pack()

    restore_button = tk.Button(edit_window, text="Restaurar", command=restore_gui_state)
    restore_button.pack()

    # Botón para salir de la ventana de edición
    exit_button = tk.Button(edit_window, text="Salir", command=exit_edit_gui)
    exit_button.pack()

def save_gui_state():
    save_column_widths()
    messagebox.showinfo("Guardar", "Cambios guardados exitosamente.")
    exit_edit_gui()

def restore_gui_state():
    load_column_widths()
    messagebox.showinfo("Restaurar", "Configuración restaurada.")
    exit_edit_gui()

def exit_edit_gui():
    # Habilitar botones después de la edición
    for widget in [search_button, play_button, download_button, directory_button, format_combobox, entry, result_listbox]:
        widget.config(state=tk.NORMAL)

# Crear ventana
window = tk.Tk()
window.title("YouTube-Downloader")
window.geometry("800x600")  # Aumentando el tamaño de la ventana
window.resizable(True, True)  # Permitiendo que la ventana sea redimensionable

# Cambiar colores de la ventana y la barra de título
window.configure(bg="#2c2c2c")  # Gris oscuro
window.tk_setPalette(background="#2c2c2c", foreground="black")

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
settings_menu.add_command(label="Edit GUI", command=edit_gui)  # Nueva opción para editar GUI
window.config(menu=settings_menu)

# Contenedor para botones y widgets relacionados
# Campo de entrada para la búsqueda de YouTube
entry = tk.Entry(window)
entry.grid(row=0, column=0, padx=(10, 3), pady=10)  # Se ajusta el padding para la entrada
entry.config(width=50, bg='white')  # Se aumenta el tamaño de la entrada y se cambia el color de fondo

# Botón para buscar en YouTube
search_button = tk.Button(window, text='Buscar', bg='white')  # Blanco
search_button.grid(row=0, column=1, padx=(3, 10), pady=10)  # Se ajusta el padding para el botón

# Botón para escuchar
play_button = tk.Button(window, text='Escuchar', bg='white')  # Blanco
play_button.grid(row=1, column=0, padx=10, pady=10)  # Se ajusta el padding para el botón

# Botón para iniciar la descarga
download_button = tk.Button(window, text='Descargar', bg='white')  # Blanco
download_button.grid(row=1, column=1, padx=10, pady=10)  # Se ajusta el padding para el botón

# Menú desplegable para seleccionar el formato de descarga
format_combobox = Combobox(window, values=["mp3", "m4a", "opus", "vorbis", "wav", "webm"])
format_combobox.grid(row=1, column=2, padx=10, pady=10)  # Se ajusta el padding para el menú desplegable

# Botón para seleccionar directorio
directory_button = tk.Button(window, text='Cambiar Directorio', bg='white')  # Blanco
directory_button.grid(row=2, column=0, columnspan=3, pady=(0, 10), padx=10, sticky="ew")  # Se ajusta el padding para el botón y se extiende a lo ancho

# Etiqueta para el directorio seleccionado
directory_label = tk.Label(window, text=output_directory, bg="#2c2c2c", fg="white") # Gris oscuro y texto blanco
directory_label.grid(row=3, column=0, columnspan=3, pady=(0, 10), padx=10, sticky="ew") # Se ajusta el padding para la etiqueta y se extiende a lo ancho

separator = tk.Frame(window, height=600, width=2, bg="black")
separator.grid(row=0, column=4, rowspan=5, padx=10, pady=10)

result_listbox = tk.Listbox(window, bg='white', fg='black', width=50) # Fondo blanco y texto negro
result_listbox.grid(row=0, column=5, rowspan=5, padx=(10, 0), pady=(0, 10), sticky="nsew")

last_language = load_language()
print("Idioma cargado:", last_language)
change_language(last_language)
print("Idioma después de cambio:", last_language)

for widget in [search_button, play_button, download_button, directory_button, format_combobox, entry, result_listbox]:
widget.bind("<ButtonPress-1>", on_button_press)
widget.bind("<B1-Motion>", on_button_drag)

window.mainloop()