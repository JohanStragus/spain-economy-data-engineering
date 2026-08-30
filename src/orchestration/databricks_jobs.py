import os
import time

import requests


# Ejecuta un Job existente de Databricks y espera hasta que termine
def run_databricks_job(job_id):

    # Obtenemos las credenciales de Databricks desde las variables de entorno
    host = os.environ["DATABRICKS_HOST"].rstrip("/")
    token = os.environ["DATABRICKS_TOKEN"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Lanzamos una nueva ejecución del Job
    response = requests.post(
        f"{host}/api/2.1/jobs/run-now",
        headers=headers,
        json={"job_id": job_id},
        timeout=30,
    )

    # Si Databricks devuelve un error HTTP, detenemos el proceso
    response.raise_for_status()

    # Databricks devuelve un run_id diferente para cada ejecución
    run_id = response.json()["run_id"]

    # Comprobamos periódicamente el estado de esa ejecución
    while True:

        response = requests.get(
            f"{host}/api/2.1/jobs/runs/get",
            headers=headers,
            params={"run_id": run_id},
            timeout=30,
        )

        # Si la respuesta falla no seguimos el código y nos quedamos aquí
        response.raise_for_status()

        state = response.json()["state"]

        life_cycle_state = state.get("life_cycle_state")
        result_state = state.get("result_state")

        # TERMINATED significa que la ejecución ya ha finalizado
        if life_cycle_state == "TERMINATED":

            # Si terminó correctamente, salimos de la función
            if result_state == "SUCCESS":
                return run_id

            # Si terminó pero falló, hacemos fallar también la tarea de Airflow
            raise RuntimeError(
                f"El Job de Databricks ha fallado. "
                f"Run ID: {run_id}, resultado: {result_state}"
            )

        # Si todavía está ejecutándose, esperamos 10 segundos
        # antes de volver a consultar su estado
        time.sleep(10)