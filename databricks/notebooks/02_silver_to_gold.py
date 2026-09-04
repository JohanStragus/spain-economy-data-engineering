# Databricks notebook source
indefinite_df = spark.table(
    "workspace.economia_espana.indefinite_silver"
)

temporary_df = spark.table(
    "workspace.economia_espana.temporary_silver"
)

# COMMAND ----------

display(
    indefinite_df.select(
        "year",
        "quarter",
        "value"
    )
)

# COMMAND ----------

display(
    temporary_df.select(
        "year",
        "quarter",
        "value"
    )
)

# COMMAND ----------

from pyspark.sql.functions import col

contracts_df = (
    indefinite_df
    .select(
        "year",
        "quarter",
        col("value").alias("indefinite")
    )
    .join(
        temporary_df.select(
            "year",
            "quarter",
            col("value").alias("temporary")
        ),
        on=["year", "quarter"],
        how="inner"
    )
)

display(contracts_df)

# COMMAND ----------

contracts_gold_df = (
    contracts_df
    .withColumn(
        "indefinite_pct",
        col("indefinite") / (col("indefinite") + col("temporary")) * 100
    )
    .withColumn(
        "temporary_pct",
        col("temporary") / (col("indefinite") + col("temporary")) * 100
    )
)

display(contracts_gold_df)

# COMMAND ----------

from pyspark.sql.functions import round

display(
    contracts_gold_df.select(
        "year",
        "quarter",
        round(
            col("indefinite_pct") + col("temporary_pct"),
            2
        ).alias("total_pct")
    )
)

# COMMAND ----------

contracts_gold_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("workspace.economia_espana.employment_contract_gold")

# COMMAND ----------

full_time_df = spark.table(
    "workspace.economia_espana.full_time_silver"
)

part_time_df = spark.table(
    "workspace.economia_espana.part_time_silver"
)

# COMMAND ----------

display(
    full_time_df.select(
        "year",
        "quarter",
        "value"
    )
)

# COMMAND ----------

display(
    part_time_df.select(
        "year",
        "quarter",
        "value"
    )
)

# COMMAND ----------

work_schedule_df = (
    full_time_df
    .select(
        "year",
        "quarter",
        col("value").alias("full_time")
    )
    .join(
        part_time_df.select(
            "year",
            "quarter",
            col("value").alias("part_time")
        ),
        on=["year", "quarter"],
        how="inner"
    )
)

display(work_schedule_df)

# COMMAND ----------

work_schedule_gold_df = (
    work_schedule_df
    .withColumn(
        "full_time_pct",
        col("full_time") / (col("full_time") + col("part_time")) * 100
    )
    .withColumn(
        "part_time_pct",
        col("part_time") / (col("full_time") + col("part_time")) * 100
    )
)

display(work_schedule_gold_df)

# COMMAND ----------

display(
    work_schedule_gold_df.select(
        "year",
        "quarter",
        round(
            col("full_time_pct") + col("part_time_pct"),
            2
        ).alias("total_pct")
    )
)

# COMMAND ----------

work_schedule_gold_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("workspace.economia_espana.work_schedule_gold")

# COMMAND ----------

salary_df = spark.table(
    "workspace.economia_espana.salary_silver"
)

cpi_df = spark.table(
    "workspace.economia_espana.cpi_silver"
)

# COMMAND ----------

display(
    salary_df.select(
        "year",
        "quarter",
        "value"
    )
)

display(
    cpi_df.select(
        "year",
        "quarter",
        "value"
    )
)

# COMMAND ----------

salary_cpi_df = (
    salary_df
    .select(
        "year",
        "quarter",
        col("value").alias("nominal_salary")
    )
    .join(
        cpi_df.select(
            "year",
            "quarter",
            col("value").alias("cpi")
        ),
        on=["year", "quarter"],
        how="inner"
    )
)

display(salary_cpi_df)

# COMMAND ----------

salary_real_gold_df = (
    salary_cpi_df
    .withColumn(
        "real_salary_base_2025",
        col("nominal_salary") * 100 / col("cpi")
    )
)

display(salary_real_gold_df)

# COMMAND ----------

display(
    salary_real_gold_df
    .filter(col("year") == 2025)
)

# COMMAND ----------

salary_real_gold_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("workspace.economia_espana.purchasing_power_gold")

# COMMAND ----------

population_df = spark.table(
    "workspace.economia_espana.population_silver"
)

gdp_df = spark.table(
    "workspace.economia_espana.gdp_real_silver"
)

# COMMAND ----------

population_quarters_df = (
    gdp_df
    .select(
        "year",
        "date",
        "quarter"
    )
    .join(
        population_df.select(
            "date",
            col("value").alias("population")
        ),
        on="date",
        how="left"
    )
    .orderBy("date")
)

display(population_quarters_df)

# COMMAND ----------

from pyspark.sql.window import Window
from pyspark.sql.functions import last, first

window_previous = (
    Window
    .orderBy("date")
    .rowsBetween(Window.unboundedPreceding, -1)
)

window_next = (
    Window
    .orderBy("date")
    .rowsBetween(1, Window.unboundedFollowing)
)

population_interpolation_df = (
    population_quarters_df
    .withColumn(
        "previous_population",
        last("population", ignorenulls=True).over(window_previous)
    )
    .withColumn(
        "next_population",
        first("population", ignorenulls=True).over(window_next)
    )
)

display(population_interpolation_df)

# COMMAND ----------

from pyspark.sql.functions import when, lit

population_gold_df = (
    population_interpolation_df
    .withColumn(
        "population_quarterly",
        when(
            col("population").isNull()
            & col("previous_population").isNotNull()
            & col("next_population").isNotNull(),
            (col("previous_population") + col("next_population")) / 2
        ).otherwise(col("population"))
    )
    .withColumn(
        "population_source",
        when(
            col("population").isNull(),
            lit("interpolated")
        ).otherwise(lit("observed"))
    )
)

display(population_gold_df)

# COMMAND ----------

population_gold_df = (
    population_gold_df
    .select(
        "year",
        "date",
        "quarter",
        "population_quarterly",
        "population_source"
    )
)

display(population_gold_df)

# COMMAND ----------

population_gold_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("workspace.economia_espana.population_quarterly_gold")

# COMMAND ----------

gdp_df = spark.table(
    "workspace.economia_espana.gdp_real_silver"
)

population_quarterly_df = spark.table(
    "workspace.economia_espana.population_quarterly_gold"
)

gdp_population_df = (
    gdp_df
    .select(
        "year",
        "quarter",
        "date",
        col("value").alias("gdp_real_index")
    )
    .join(
        population_quarterly_df.select(
            "year",
            "quarter",
            "population_quarterly",
            "population_source"
        ),
        on=["year", "quarter"],
        how="inner"
    )
    .orderBy("date")
)

display(gdp_population_df)

# COMMAND ----------

base_row = (
    gdp_population_df
    .filter(
        (col("year") == 2015) &
        (col("quarter") == "T1")
    )
    .select(
        "gdp_real_index",
        "population_quarterly"
    )
    .first()
)

gdp_base = base_row["gdp_real_index"]
population_base = base_row["population_quarterly"]

print("PIB base:", gdp_base)
print("Población base:", population_base)

# COMMAND ----------

gdp_per_capita_gold_df = (
    gdp_population_df
    .withColumn(
        "gdp_per_capita_index",
        (
            (col("gdp_real_index") / gdp_base)
            /
            (col("population_quarterly") / population_base)
        ) * 100
    )
)

display(gdp_per_capita_gold_df)

# COMMAND ----------

gdp_per_capita_gold_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("workspace.economia_espana.gdp_per_capita_gold")