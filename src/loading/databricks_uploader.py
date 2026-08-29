import os
from pathlib import Path

import requests

from config.series import SERIES


# Obtenemos la raíz del proyecto.
# Desde este archivo subimos dos niveles:
# src/loading/databricks_uploader.py -> raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Ruta del Volume Bronze dentro de Databricks
DATABRICKS_VOLUME = "/Volumes/workspace/economia_espana/bronze"


# Función encargada de subir un único archivo a Databricks
def upload_file(local_path, remote_filename):

    # Obtenemos las credenciales desde las variables de entorno
    # guardadas en airflow/.env
    host = os.environ["DATABRICKS_HOST"].rstrip("/")
    token = os.environ["DATABRICKS_TOKEN"]

    # Construimos la URL de la Files API de Databricks
    # overwrite=true permite reemplazar el archivo si ya existe
    url = (
        f"{host}/api/2.0/fs/files"
        f"{DATABRICKS_VOLUME}/{remote_filename}?overwrite=true"
    )

    # Abrimos el archivo local en modo binario para enviarlo a Databricks
    with local_path.open("rb") as file:

        # Enviamos el archivo mediante una petición PUT
        response = requests.put(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/octet-stream",
            },
            data=file,
            timeout=30,
        )

    # Si Databricks devuelve un error HTTP, detenemos el proceso
    response.raise_for_status()


# Función encargada de subir todos los JSON de la capa Bronze
def upload_all_bronze():

    # Ruta local donde tenemos los JSON extraídos del INE
    bronze_dir = PROJECT_ROOT / "data" / "bronze"

    # Recorremos las 10 series definidas en config/series.py
    for name in SERIES:

        # Por ejemplo:
        # name = "gdp_real"
        # filename = "gdp_real.json"
        filename = f"{name}.json"

        # Construimos la ruta completa del archivo local
        local_path = bronze_dir / filename

        # Comprobamos que el archivo exista antes de intentar subirlo
        if not local_path.exists():
            raise FileNotFoundError(f"No existe el archivo: {local_path}")

        # Subimos el archivo al Volume Bronze de Databricks
        upload_file(local_path, filename)