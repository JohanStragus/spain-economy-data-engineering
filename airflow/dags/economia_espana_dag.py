import os

import pendulum

from airflow.sdk import dag, task

from src.extraction.ine_client import extract_all_series
from src.loading.databricks_uploader import upload_all_bronze
from src.orchestration.databricks_jobs import run_databricks_job
from src.loading.databricks_downloader import download_all_gold


# Definimos el DAG y su configuración en Airflow
@dag(
    dag_id="economia_espana_pipeline",
    schedule="0 0 * * *",  # Ejecución para las 00:00 mientras docker y el pc esten encendidos
    start_date=pendulum.datetime(2026, 1, 1, tz="Europe/Madrid"),
    catchup=False,  # No ejecutar periodos anteriores automáticamente
    tags=["economia", "espana", "ine"],
)
def economia_espana_pipeline():

    # Tarea 1:
    # Extrae las 10 series económicas desde la API del INE
    # y guarda los JSON en data/bronze
    @task
    def extract_ine_data():
        extract_all_series()

    # Tarea 2:
    # Sube los 10 JSON de Bronze local
    # al Volume Bronze de Databricks
    @task
    def upload_bronze_to_databricks():
        upload_all_bronze()

    # Tarea 3:
    # Lanza el Job de Databricks que ejecuta
    # el notebook 01_bronze_to_silver
    @task
    def run_bronze_to_silver():

        # Las variables de entorno siempre se leen como texto,
        # por eso convertimos el Job ID a entero
        job_id = int(
            os.environ["DATABRICKS_BRONZE_TO_SILVER_JOB_ID"]
        )

        # Ejecutamos el Job y esperamos hasta que termine
        run_databricks_job(job_id)

    # Tarea 4:
    # Lanza el Job de Databricks que ejecuta
    # el notebook 02_silver_to_gold
    @task
    def run_silver_to_gold():

        # Obtenemos el Job ID de Silver -> Gold desde las variables
        # de entorno y lo convertimos de texto a entero
        job_id = int(
            os.environ["DATABRICKS_SILVER_TO_GOLD_JOB_ID"]
        )

        # Ejecutamos el Job y esperamos hasta que termine
        run_databricks_job(job_id)

    # Tarea 5:
    # Lanza el Job de Databricks que exporta
    # las 5 tablas Gold a CSV dentro del Volume gold_exports
    @task
    def run_export_gold():

        # Obtenemos el Job ID desde las variables de entorno
        # y lo convertimos de texto a entero
        job_id = int(
            os.environ["DATABRICKS_EXPORT_GOLD_JOB_ID"]
        )

        # Ejecutamos el Job y esperamos hasta que termine
        run_databricks_job(job_id)

    # Tarea 6:
    # Descarga los 5 CSV Gold desde el Volume de Databricks
    # hasta la carpeta local data/gold
    @task
    def download_gold_to_local():
        download_all_gold()

    # Creamos las tres tareas dentro del DAG
    extract_task = extract_ine_data()
    upload_task = upload_bronze_to_databricks()
    silver_task = run_bronze_to_silver()
    gold_task = run_silver_to_gold()
    export_task = run_export_gold()
    download_task = download_gold_to_local()

    # Definimos el orden de ejecución del pipeline
    extract_task >> upload_task >> silver_task >> gold_task >> export_task >> download_task


# Creamos la instancia del DAG para que Airflow pueda descubrirlo
economia_espana_pipeline()