from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.properties import BooleanProperty

from youtubesearchpython import Search
import subprocess
import webbrowser

class SelectableRecycleBoxLayout(LayoutSelectionBehavior, RecycleBoxLayout):
    """ Adds selection and focus behavior to the view. """
    pass

class SelectableLabel(RecycleDataViewBehavior, Label):
    """ Add selection support to the Label """
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        """ Add selection on touch down """
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

class YouTubeDownloaderApp(App):
    def build(self):
        self.output_directory = None
        self.video_ids = []

        layout = BoxLayout(orientation='vertical', spacing=10, padding=(10, 10))

        self.entry = TextInput(hint_text='Ingrese la búsqueda', multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.entry)

        search_button = Button(text='Buscar en YouTube', on_press=self.search_youtube, size_hint_y=None, height=50)
        layout.add_widget(search_button)

        self.result_listbox = RecycleView(size_hint=(1, 1))
        layout.add_widget(self.result_listbox)

        button_layout = BoxLayout(spacing=10, size_hint_y=None, height=50)

        directory_button = Button(text='Seleccionar directorio', on_press=self.select_directory, size_hint=(0.3, 1))
        button_layout.add_widget(directory_button)

        download_button = Button(text='Descargar', on_press=self.download_audio, size_hint=(0.3, 1))
        button_layout.add_widget(download_button)

        play_button = Button(text='Escuchar', on_press=self.play_video, size_hint=(0.3, 1))
        button_layout.add_widget(play_button)

        layout.add_widget(button_layout)

        self.directory_label = Label(text='Directorio de salida:')
        layout.add_widget(self.directory_label)

        return layout

    def select_directory(self, instance):
        file_chooser = FileChooserListView()
        file_chooser.bind(on_submit=self.on_directory_selected)
        popup = Popup(title='Seleccionar directorio', content=file_chooser, size_hint=(0.9, 0.9))
        popup.open()

    def on_directory_selected(self, instance, selection, touch):
        if selection:
            self.output_directory = selection[0]
            self.directory_label.text = f'Directorio de salida: {self.output_directory}'

    def search_youtube(self, instance):
        search_query = self.entry.text
        all_search = Search(search_query, limit=10)
        results = all_search.result()['result']
        self.result_listbox.data = []

        for i, result in enumerate(results, start=1):
            self.result_listbox.data.append({'text': f"{i}. {result['title']}", 'selectable': True})

    def download_audio(self, instance):
        if self.output_directory:
            selected_index = self.result_listbox.layout_manager.selected_nodes
            if selected_index:
                selected_id = self.video_ids[selected_index[0]]
                video_url = f"https://www.youtube.com/watch?v={selected_id}"
                ffmpeg_path = "FFmpeg/bin"  # Carpeta FFmpeg en el mismo directorio que el archivo
                download_command = f"youtube-dl --ffmpeg-location {ffmpeg_path} -o {self.output_directory}/%(title)s.%(ext)s --extract-audio --audio-format mp3 {video_url}"
                subprocess.Popen(download_command, shell=True)

    def play_video(self, instance):
        selected_index = self.result_listbox.layout_manager.selected_nodes
        if selected_index:
            selected_id = self.video_ids[selected_index[0]]
            video_url = f"https://www.youtube.com/watch?v={selected_id}"
            webbrowser.open(video_url)

if __name__ == '__main__':
    YouTubeDownloaderApp().run()
