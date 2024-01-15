# search.py
import os
import json
from youtube_search import YoutubeSearch

def buscar_youtube(query, historial_path="history"):
    # Crear la carpeta de historial si no existe
    os.makedirs(historial_path, exist_ok=True)

    # Obtener la lista de archivos de historial
    historial_archivos = os.listdir(historial_path)

    # Determinar el siguiente número de archivo para la nueva búsqueda
    numero_archivo = 1
    while f"busqueda-{numero_archivo}.json" in historial_archivos:
        numero_archivo += 1

    # Ruta completa del nuevo archivo de historial
    nuevo_archivo = os.path.join(historial_path, f"busqueda-{numero_archivo}.json")

    # Realizar la búsqueda
    results = YoutubeSearch(query, max_results=10).to_json()

    # Guardar los resultados en el archivo de historial
    with open(nuevo_archivo, 'w') as file:
        json.dump(results, file)

    # Devolver los resultados
    return results
