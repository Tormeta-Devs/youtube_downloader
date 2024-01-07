from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.recycleview import RecycleView
from youtubesearchpython import Search
import subprocess
import webbrowser

class YouTubeDownloaderApp(App):
    def build(self):
        self.output_directory = None
        self.video_ids = []

        layout = BoxLayout(orientation='vertical', spacing=10, padding=(10, 10))

        self.entry = TextInput(hint_text='Ingrese la búsqueda', multiline=False, size_hint_y=None, height=30)
        layout.add_widget(self.entry)

        search_button = Button(text='Buscar en YouTube', on_press=self.search_youtube)
        layout.add_widget(search_button)

        self.result_listbox = RecycleView(size_hint=(None, None), size=(400, 200))
        layout.add_widget(self.result_listbox)

        button_layout = BoxLayout(spacing=10)

        directory_button = Button(text='Seleccionar directorio', on_press=self.select_directory)
        button_layout.add_widget(directory_button)

        download_button = Button(text='Descargar', on_press=self.download_audio)
        button_layout.add_widget(download_button)

        play_button = Button(text='Escuchar', on_press=self.play_video)
        button_layout.add_widget(play_button)

        layout.add_widget(button_layout)

        self.directory_label = Label(text='Directorio de salida:')
        layout.add_widget(self.directory_label)

        return layout

    def select_directory(self, instance):
        self.output_directory = '/'.join(self.open_dir('Seleccionar directorio'))

    def search_youtube(self, instance):
        search_query = self.entry.text
        all_search = Search(search_query, limit=10)
        results = all_search.result()['result']
        self.result_listbox.data = []

        for i, result in enumerate(results, start=1):
            self.result_listbox.data.append({'text': f"{i}. {result['title']}"})
            self.video_ids.append(result['id'])

    def download_audio(self, instance):
        if self.output_directory:
            selected_index = self.result_listbox.selected_nodes
            if selected_index:
                selected_id = self.video_ids[selected_index[0]]
                video_url = f"https://www.youtube.com/watch?v={selected_id}"
                ffmpeg_path = "FFmpeg/bin"  # Carpeta FFmpeg en el mismo directorio que el archivo
                download_command = f"youtube-dl --ffmpeg-location {ffmpeg_path} -o {self.output_directory}/%(title)s.%(ext)s --extract-audio --audio-format mp3 {video_url}"
                subprocess.Popen(download_command, shell=True)

    def play_video(self, instance):
        selected_index = self.result_listbox.selected_nodes
        if selected_index:
            selected_id = self.video_ids[selected_index[0]]
            video_url = f"https://www.youtube.com/watch?v={selected_id}"
            webbrowser.open(video_url)

if __name__ == '__main__':
    YouTubeDownloaderApp().run()
