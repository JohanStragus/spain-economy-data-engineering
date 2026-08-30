import os
from pathlib import Path

import requests


# Obtenemos la raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Volume de Databricks donde están los CSV Gold exportados
DATABRICKS_GOLD_VOLUME = (
    "/Volumes/workspace/economia_espana/gold_exports"
)


# Archivos Gold que queremos descargar
GOLD_FILES = [
    "employment_contract_gold.csv",
    "work_schedule_gold.csv",
    "purchasing_power_gold.csv",
    "population_quarterly_gold.csv",
    "gdp_per_capita_gold.csv",
]


# Descarga un único archivo desde Databricks
def download_file(remote_filename, local_path):

    # Obtenemos las credenciales desde las variables de entorno
    host = os.environ["DATABRICKS_HOST"].rstrip("/")
    token = os.environ["DATABRICKS_TOKEN"]

    # Construimos la URL del archivo dentro del Volume
    url = (
        f"{host}/api/2.0/fs/files"
        f"{DATABRICKS_GOLD_VOLUME}/{remote_filename}"
    )

    # Pedimos el archivo a Databricks
    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {token}",
        },
        timeout=30,
    )

    # Si Databricks devuelve un error, detenemos el proceso
    response.raise_for_status()

    # Guardamos el contenido recibido como archivo local
    with local_path.open("wb") as file:
        file.write(response.content)


# Descarga todos los CSV Gold al repositorio local
def download_all_gold():

    # Carpeta local donde guardaremos los resultados Gold
    gold_dir = PROJECT_ROOT / "data" / "gold"

    # La creamos si todavía no existe
    gold_dir.mkdir(parents=True, exist_ok=True)

    # Recorremos los 5 CSV Gold
    for filename in GOLD_FILES:

        # Construimos la ruta local de destino
        local_path = gold_dir / filename

        # Descargamos el archivo
        download_file(filename, local_path)