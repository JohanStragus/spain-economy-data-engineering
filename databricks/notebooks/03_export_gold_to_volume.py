# Databricks notebook source
# Ruta del Volume donde guardaremos las exportaciones Gold
GOLD_EXPORT_VOLUME = "/Volumes/workspace/economia_espana/gold_exports"


# Tablas Gold que queremos exportar
gold_tables = [
    "employment_contract_gold",
    "work_schedule_gold",
    "purchasing_power_gold",
    "population_quarterly_gold",
    "gdp_per_capita_gold",
]


# Recorremos cada tabla Gold
for table_name in gold_tables:

    # Construimos el nombre completo de la tabla en Unity Catalog
    full_table_name = f"workspace.economia_espana.{table_name}"

    # Leemos la tabla Gold y ordenamos los datos por año y trimestre
    # para que el CSV mantenga siempre un orden estable
    gold_df = (
        spark.table(full_table_name)
        .orderBy("year", "quarter")
    )

    # Convertimos el DataFrame de Spark a Pandas.
    # En nuestro caso las tablas son muy pequeñas, por lo que es adecuado.
    gold_pandas_df = gold_df.toPandas()

    # Construimos la ruta del archivo CSV
    export_path = f"{GOLD_EXPORT_VOLUME}/{table_name}.csv"

    # Guardamos un único CSV sin la columna de índice de Pandas
    gold_pandas_df.to_csv(
        export_path,
        index=False
    )

    # Mostramos qué archivo se ha exportado correctamente
    print(f"Exportado: {table_name}.csv")


print("Exportación Gold completada")