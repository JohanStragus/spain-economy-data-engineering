# Databricks notebook source
bronze_path = "/Volumes/workspace/economia_espana/bronze"

files = dbutils.fs.ls(bronze_path)

display(files)

# COMMAND ----------

gdp_path = f"{bronze_path}/gdp_real.json"

gdp_raw_df = (spark.read.option("multiline", "true").json(gdp_path))

# COMMAND ----------

gdp_raw_df.printSchema()

# COMMAND ----------

display(
    gdp_raw_df.select(
        "COD",
        "Nombre",
        "T3_Escala",
        "T3_Unidad",
        "Data"
    )
)

# COMMAND ----------

from pyspark.sql.functions import explode

gdp_exploded_df =  gdp_raw_df.select(
    "COD",
    "Nombre",
    "T3_Escala",
    "T3_Unidad",
    explode("Data").alias("data")
)

display(gdp_exploded_df)

# COMMAND ----------

gdp_flat_df = gdp_exploded_df.select(
    "COD",
    "Nombre",
    "T3_Escala",
    "T3_Unidad",
    "data.Anyo",
    "data.Fecha",
    "data.T3_Periodo",
    "data.T3_TipoDato",
    "data.Valor"
)

display(gdp_flat_df)

# COMMAND ----------

gdp_silver_df = (
    gdp_flat_df
    .withColumnRenamed("COD", "series_code")
    .withColumnRenamed("Nombre", "series_name")
    .withColumnRenamed("T3_Escala", "scale")
    .withColumnRenamed("T3_Unidad", "unit")
    .withColumnRenamed("Anyo", "year")
    .withColumnRenamed("Fecha", "date")
    .withColumnRenamed("T3_Periodo", "quarter")
    .withColumnRenamed("T3_TipoDato", "data_type")
    .withColumnRenamed("Valor", "value")
)

display(gdp_silver_df)

# COMMAND ----------

from pyspark.sql.functions import to_date, substring

gdp_silver_df = gdp_silver_df.withColumn(
    "date",
    to_date(substring("date", 1, 10), "yyyy-MM-dd")
)

gdp_silver_df.printSchema()

# COMMAND ----------

from pyspark.sql.functions import col

print("Filas:", gdp_silver_df.count())
print("Valores nulos:", gdp_silver_df.filter(col("value").isNull()).count())

display(
    gdp_silver_df.select(
        "year",
        "quarter",
        "date",
        "value",
        "unit"
    )
)

# COMMAND ----------

gdp_silver_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("workspace.economia_espana.gdp_real_silver")

# COMMAND ----------

gdp_saved_df = spark.table(
    "workspace.economia_espana.gdp_real_silver"
)

print("Filas guardadas:", gdp_saved_df.count())

display(gdp_saved_df)

# COMMAND ----------

from pyspark.sql.functions import explode, to_date, substring

def normalize_ine_series(file_name):
    path = f"{bronze_path}/{file_name}"

    raw_df = (
        spark.read
        .option("multiline", "true")
        .json(path)
    )

    exploded_df = raw_df.select(
        "COD",
        "Nombre",
        "T3_Escala",
        "T3_Unidad",
        explode("Data").alias("data")
    )

    normalized_df = exploded_df.select(
        "COD",
        "Nombre",
        "T3_Escala",
        "T3_Unidad",
        "data.Anyo",
        "data.Fecha",
        "data.T3_Periodo",
        "data.T3_TipoDato",
        "data.Valor"
    )

    normalized_df = (
        normalized_df
        .withColumnRenamed("COD", "series_code")
        .withColumnRenamed("Nombre", "series_name")
        .withColumnRenamed("T3_Escala", "scale")
        .withColumnRenamed("T3_Unidad", "unit")
        .withColumnRenamed("Anyo", "year")
        .withColumnRenamed("Fecha", "date")
        .withColumnRenamed("T3_Periodo", "period")
        .withColumnRenamed("T3_TipoDato", "data_type")
        .withColumnRenamed("Valor", "value")
        .withColumn(
            "date",
            to_date(substring("date", 1, 10), "yyyy-MM-dd")
        )
    )

    return normalized_df

# COMMAND ----------

employed_silver_df = normalize_ine_series("employed.json")

display(employed_silver_df)

# COMMAND ----------

print("Filas:", employed_silver_df.count())
print(
    "Valores nulos:",
    employed_silver_df.filter(col("value").isNull()).count()
)

employed_silver_df.printSchema()

# COMMAND ----------

def prepare_quarterly_series(file_name):
    df = normalize_ine_series(file_name)

    return df.withColumnRenamed("period", "quarter")

# COMMAND ----------

gdp_silver_df = prepare_quarterly_series("gdp_real.json")

display(gdp_silver_df)

# COMMAND ----------

gdp_silver_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("workspace.economia_espana.gdp_real_silver")

# COMMAND ----------

employed_silver_df = prepare_quarterly_series("employed.json")

display(employed_silver_df)

# COMMAND ----------

employed_silver_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("workspace.economia_espana.employed_silver")

# COMMAND ----------

quarterly_series = {
    "unemployment_rate": "unemployment_rate.json",
    "indefinite": "indefinite.json",
    "temporary": "temporary.json",
    "full_time": "full_time.json",
    "part_time": "part_time.json",
    "salary": "salary.json"
}

for name, file_name in quarterly_series.items():

    df = prepare_quarterly_series(file_name)

    print(
        name,
        "| filas:", df.count(),
        "| nulos:", df.filter(col("value").isNull()).count()
    )

    df.write \
        .format("delta") \
        .mode("overwrite") \
        .saveAsTable(
            f"workspace.economia_espana.{name}_silver"
        )

# COMMAND ----------

cpi_normalized_df = normalize_ine_series("cpi.json")

display(cpi_normalized_df)

# COMMAND ----------

from pyspark.sql.functions import quarter, concat, lit

cpi_with_quarter_df = cpi_normalized_df.withColumn(
    "quarter",
    concat(lit("T"), quarter("date"))
)

display(
    cpi_with_quarter_df.select(
        "year",
        "date",
        "period",
        "quarter",
        "value"
    )
)

# COMMAND ----------

from pyspark.sql.functions import avg, count, min as spark_min, col

cpi_quarterly_df = (
    cpi_with_quarter_df
    .groupBy(
        "series_code",
        "series_name",
        "scale",
        "unit",
        "year",
        "quarter",
        "data_type"
    )
    .agg(
        avg("value").alias("value"),
        count("*").alias("months_in_quarter"),
        spark_min("date").alias("date")
    )
    .filter(col("months_in_quarter") == 3)
    .orderBy("date")
)

display(cpi_quarterly_df)

# COMMAND ----------

cpi_silver_df = cpi_quarterly_df.drop("months_in_quarter")

display(cpi_silver_df)

# COMMAND ----------

cpi_silver_df = cpi_silver_df.select(
    "series_code",
    "series_name",
    "scale",
    "unit",
    "year",
    "date",
    "quarter",
    "data_type",
    "value"
)

display(cpi_silver_df)

# COMMAND ----------

cpi_silver_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("workspace.economia_espana.cpi_silver")

# COMMAND ----------

population_normalized_df = normalize_ine_series("population.json")

display(
    population_normalized_df.select(
        "year",
        "date",
        "period",
        "value",
        "unit",
        "scale"
    )
)

# COMMAND ----------

population_silver_df = population_normalized_df

print("Filas:", population_silver_df.count())
print(
    "Valores nulos:",
    population_silver_df.filter(col("value").isNull()).count()
)

display(population_silver_df)

# COMMAND ----------

population_silver_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("workspace.economia_espana.population_silver")