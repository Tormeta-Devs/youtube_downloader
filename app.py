import os
import json
import subprocess
import tkinter as tk
from tkinter import filedialog
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button

# Importar buscar_youtube desde extras.search
from extras.search import buscar_youtube

# Importar DropDown desde kivy
from kivy.uix.dropdown import DropDown

# Clase para un botón con imagen
class ImageButton(ButtonBehavior, Image):
    pass

class youtube_downloader(App):
    def build(self):
        self.title = "YouTube-Downloader" 
        self.icon = "extras\main.ico"
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Casilla de entrada de texto
        self.text_input = TextInput(multiline=False)
        layout.add_widget(self.text_input)

        # Botón de búsqueda
        self.btn_buscar = Button(text="Buscar en YouTube", size_hint_y=None, height=40)
        self.btn_buscar.bind(on_press=self.buscar_en_youtube)
        layout.add_widget(self.btn_buscar)

        # Botón para elegir directorio de descarga
        btn_elegir_directorio = Button(text="Elegir Directorio", size_hint_y=None, height=40, on_press=self.elegir_directorio)
        layout.add_widget(btn_elegir_directorio)

        # Botón de Descargar
        btn_descargar = Button(text="Descargar", size_hint_y=None, height=40, on_press=self.descargar_video)
        layout.add_widget(btn_descargar)

        # Botón para acceder al historial
        btn_historial = Button(text="Historial", size_hint_y=None, height=40, on_press=self.mostrar_historial)
        layout.add_widget(btn_historial)

        # Resultados de la búsqueda
        self.resultados_layout = ScrollView()  
        self.resultados_inner_layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        self.resultados_inner_layout.bind(minimum_height=self.resultados_inner_layout.setter('height'))
        self.resultados_layout.add_widget(self.resultados_inner_layout)
        layout.add_widget(self.resultados_layout)

        # Desactivar el botón de búsqueda al inicio
        self.btn_buscar_disabled = False  # Variable para controlar si el botón de búsqueda está desactivado

        # Lista desplegable para el historial
        self.dropdown_historial = DropDown()

        # Lista de formatos permitidos
        formatos_permitidos = ["3gp", "aac", "flv", "m4a", "mp3", "mp4", "ogg", "wav", "webm"]

        # Lista desplegable para los formatos
        self.dropdown_formatos = DropDown()

        # Agregar los formatos a la lista desplegable
        for formato in formatos_permitidos:
            btn_formato = Button(text=formato, size_hint_y=None, height=30)
            btn_formato.bind(on_release=self.seleccionar_formato)
            self.dropdown_formatos.add_widget(btn_formato)

        return layout

    def buscar_en_youtube(self, instance):
        if not self.btn_buscar_disabled:
            # Obtener el texto de la casilla
            query = self.text_input.text

            # Llamar a la función en search.py
            resultados = buscar_youtube(query)

            # Limpiar resultados anteriores
            self.resultados_inner_layout.clear_widgets()

            # Mostrar los nuevos resultados
            for video in resultados['videos']:
                # Crear widgets para cada resultado
                thumbnail = ImageButton(source=video['thumbnails'][0], size=(100, 100), size_hint=(None, None))
                title_label = Label(text=video['title'])
                channel_label = Label(text=f"Canal: {video['channel']}")
                duration_label = Label(text=f"Duracion: {video['duration']}")

                # Botón de Descargar
                btn_descargar = Button(text="Descargar", size_hint_y=None, height=30, on_press=self.descargar_video)

                # Casilla de opciones para el formato
                opciones_formato = TextInput(multiline=False, hint_text="Formato: mp4", size_hint_y=None, height=30)

                # Añadir todo al diseño
                self.resultados_inner_layout.add_widget(thumbnail)
                self.resultados_inner_layout.add_widget(title_label)
                self.resultados_inner_layout.add_widget(channel_label)
                self.resultados_inner_layout.add_widget(duration_label)
                self.resultados_inner_layout.add_widget(btn_descargar)
                self.resultados_inner_layout.add_widget(opciones_formato)

    def mostrar_historial(self, instance):
        # Limpiar resultados anteriores
        self.resultados_inner_layout.clear_widgets()

        # Cargar el contenido del archivo de historial y mostrar los resultados
        archivo_path = os.path.join("extras/history", instance.text)
        with open(archivo_path, 'r') as archivo:
            resultados = json.load(archivo)

            # Limpiar resultados anteriores
            self.resultados_inner_layout.clear_widgets()

            # Mostrar los nuevos resultados
            for video in resultados['videos']:
                # Crear widgets para cada resultado
                thumbnail = ImageButton(source=video['thumbnails'][0], size=(100, 100), size_hint=(None, None))
                title_label = Label(text=video['title'])
                channel_label = Label(text=f"Canal: {video['channel']}")
                duration_label = Label(text=f"Duracion: {video['duration']}")

                # Botón de Descargar
                btn_descargar = Button(text="Descargar", size_hint_y=None, height=30, on_press=self.descargar_video)

                # Casilla de opciones para el formato
                opciones_formato = TextInput(multiline=False, hint_text="Formato: mp4", size_hint_y=None, height=30)

                # Añadir todo al diseño
                self.resultados_inner_layout.add_widget(thumbnail)
                self.resultados_inner_layout.add_widget(title_label)
                self.resultados_inner_layout.add_widget(channel_label)
                self.resultados_inner_layout.add_widget(duration_label)
                self.resultados_inner_layout.add_widget(btn_descargar)
                self.resultados_inner_layout.add_widget(opciones_formato)

    def seleccionar_formato(self, instance):
        # Cerrar la lista desplegable
        self.dropdown_formatos.dismiss()

        # Obtener el formato seleccionado desde el texto del botón
        formato_seleccionado = instance.text

        # Hacer algo con el formato seleccionado (puedes almacenarlo en una variable, etc.)
        print(f"Formato seleccionado: {formato_seleccionado}")

        # Modificar la casilla de opciones con el formato seleccionado
        self.resultados_inner_layout.children[-1].text = formato_seleccionado

    def elegir_directorio(self, instance):
        # Cuadro de diálogo para seleccionar un directorio
        root = tk.Tk()
        root.withdraw()  # Ocultar la ventana principal de tkinter

        directorio_seleccionado = filedialog.askdirectory()

        if directorio_seleccionado:
            print(f"Directorio seleccionado: {directorio_seleccionado}")

            # Guardar el directorio seleccionado para su uso posterior
            self.directorio_descarga = directorio_seleccionado

    def descargar_video(self, instance):
        # Obtener el formato seleccionado desde la casilla de opciones
        formato_elegido = self.resultados_inner_layout.children[-1].text

        # Obtener el ID del video desde el título del primer resultado
        id_video = self.resultados_inner_layout.children[1].text.split(": ")[1]

        # Obtener el directorio de descarga
        output_directory = getattr(self, 'directorio_descarga', "downloads/")

        # Comando de descarga
        download_command = f"python extras/down.py {id_video} {formato_elegido} {output_directory}"

        try:
            # Ejecutar el comando de descarga en un proceso separado
            subprocess.run(download_command, shell=True, check=True)
            print("Descarga exitosa.")
        except subprocess.CalledProcessError as e:
            print(f"Error en la descarga: {e}")

if __name__ == '__main__':
    youtube_downloader().run()
