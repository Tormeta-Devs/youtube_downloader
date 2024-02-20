import os
import subprocess
import threading

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.popup import Popup

from xml.etree import ElementTree as ET
from youtubesearchpython import Search
import webbrowser

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

class YouTubeDownloader(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.orientation = "vertical"
        
        # Crear instancia de Popup para mostrar mensajes
        self.popup = Popup(title='', content=Label(text=''), size_hint=(None, None), size=(400, 200))

        # Botones
        self.search_button = Button(text='', on_press=self.search_youtube)
        self.directory_button = Button(text='', on_press=self.select_directory)
        self.download_button = Button(text='', on_press=self.download_audio_or_video)
        self.play_button = Button(text='', on_press=self.play_audio_or_video)

        # Cargar los mensajes en el idioma predeterminado
        self.last_language = self.load_language()
        self.change_language(self.last_language)

    def load_language(self):
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                return f.read().strip()
        else:
            return default_language

    def save_language(self, language):
        with open(config_file, "w") as f:
            f.write(language)

    def load_messages(self, language):
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

    def change_language(self, language):
        global messages, language_index
        messages = self.load_messages(language)
        language_index = languages.index(language)
        self.save_language(language)
        self.update_button_texts()

    def check_ffmpeg_update(self):
        subprocess.Popen(["winget", "upgrade", "ffmpeg"]).wait()
        self.popup.title = messages.get('ffmpeg_update_title', 'FFmpeg Update')
        self.popup.content.text = messages.get('ffmpeg_update_message', 'FFmpeg ha sido actualizado.')
        self.popup.open()

    def search_youtube(self, instance):
        result_listbox.data = []  # Limpiar la lista de resultados
        video_ids.clear()
        allSearch = Search(self.search_query.text, limit=10)
        results = allSearch.result()['result']
        for result in results:
            video_ids.append(result['id'])
            result_listbox.data.append({'text': result['title'], 'size_hint_y': None, 'height': 40})

    def download_audio_or_video(self, instance):
        if result_listbox.selected_nodes:
            selected_index = result_listbox.selected_nodes[0]
            selected_id = video_ids[selected_index]
            video_url = f"https://www.youtube.com/watch?v={selected_id}"
            selected_format = format_spinner.text or default_format
            download_command = f"youtube-dl -o \"{output_directory}/%(title)s.%(ext)s\" -x --audio-format {selected_format} {video_url}" if selected_format != "webm" else f"youtube-dl -o \"{output_directory}/%(title)s.%(ext)s\" -f bestvideo {video_url}"
            threading.Thread(target=self.perform_download, args=(download_command,)).start()

    def perform_download(self, download_command):
        subprocess.Popen(download_command, shell=True).wait()
        self.download_counter += 1
        self.update_title()

    def update_title(self):
        self.title = f"{messages.get('window_title', 'YouTube-Downloader')} | FFmpeg: {self.get_ffmpeg_version()} | Descargas: {download_counter}"

    def get_ffmpeg_version(self):
        try:
            version_output = subprocess.check_output(["ffmpeg", "-version"]).decode("utf-8")
            version_line = version_output.splitlines()[0]
            version = version_line.split("version ")[1].split(" ")[0]
            return version
        except Exception as e:
            print(f"Error al obtener la versión de FFmpeg: {e}")
            return "Desconocida"

    def update_button_texts(self):
        self.search_button.text = messages.get('search_button', 'Buscar en YouTube')
        self.directory_button.text = messages.get('directory_button', 'Cambiar Directorio')
        self.download_button.text = messages.get('download_button', 'Descargar')
        self.play_button.text = messages.get('play_button', 'Escuchar')

        # Actualizar texto del menú desplegable de idiomas
        language_spinner.text = messages.get(f'language_name_{languages[language_index]}', languages[language_index].capitalize())

class YouTubeDownloaderApp(App):
    def build(self):
        return YouTubeDownloader()

if __name__ == "__main__":
    YouTubeDownloaderApp().run()
