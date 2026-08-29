import pendulum

from airflow.sdk import dag, task

from src.extraction.ine_client import extract_all_series
from src.loading.databricks_uploader import upload_all_bronze


# Definimos el DAG y su configuración en Airflow
@dag(
    dag_id="economia_espana_pipeline",
    schedule=None,  # Por ahora solo se ejecutará manualmente
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
    # Sube los 10 JSON de Bronze local al Volume Bronze de Databricks
    @task
    def upload_bronze_to_databricks():
        upload_all_bronze()

    # Creamos las dos tareas dentro del DAG
    extract_task = extract_ine_data()
    upload_task = upload_bronze_to_databricks()

    # Definimos el orden de ejecución:
    # primero extracción y, cuando termine correctamente, subida a Databricks
    extract_task >> upload_task


# Creamos la instancia del DAG para que Airflow pueda descubrirlo
economia_espana_pipeline()