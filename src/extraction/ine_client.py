import json
from pathlib import Path

import requests
from config.series import SERIES, START_DATE, END_DATE

# Url principal para las peticiones
BASE_URL = "https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE"

# Función para escribir el código de los datos serie que queremos investigar
def get_series(series_code):

    # URL con serie_code variable, dependiendo de lo que queramos buscar
    url = f"{BASE_URL}/{series_code}"

    # parámetros para la URL (Documentado en la API de INE)
    params = {
        "date": f"{START_DATE}:{END_DATE}",
        "tip": "A",
    }

    # realizamos la petición a la API 
    response = requests.get(url, params=params, timeout=30,)

    # si ocurre un error no continuar el programa
    response.raise_for_status()

    # Convertimos el JSON recibido en objetos Python
    return response.json()

# Función para guardar los datos recibidos a Bronze
def save_json(data, filename):

    # Directorio donde guardaremos los datos
    bronze_dir = Path("data/bronze")

    # Por si acaso la carpeta o ruta no existe la creamos, y si existe no pasa nada
    bronze_dir.mkdir(parents=True, exist_ok=True)

    # Ruta final del archivo
    file_path = bronze_dir / filename

    # Guardamos en dicha ruta el fichero JSON
    with file_path.open("w", encoding="utf-8") as file:

        # Convertimos el objeto Python a JSON y lo escribimos en el archivo
        json.dump(data, file, ensure_ascii=False, indent=4)

# Ejecutamos este bloque solo cuando este archivo se ejecuta directamente
if __name__ == "__main__":

    # Recorremos todo el diccionario de series
    for name, code in SERIES.items():

        # Obtenemos los datos a partir del código de serie
        data = get_series(code)

        # Una vez con los datos obtenidos, los guardamos de objeto a JSON en Bronze
        save_json(data, f"{name}.json")