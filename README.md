# Spain Economy Data Engineering

Data Engineering project focused on analysing the evolution of the Spanish economy between **2015 and 2026** using official public data.

The main goal is to answer a simple question:

> **Has the Spanish economy really improved for the average citizen?**

The project combines economic analysis with a complete Data Engineering workflow using official data from the **Instituto Nacional de Estadística (INE)**.

---

## Project Questions

The analysis is divided into four main areas.

### 1. Economic Production

Indicators:

- Real GDP
- Population
- Real GDP per capita index

Main question:

> Is Spain producing more in real terms, and has that improvement also occurred per inhabitant?

---

### 2. Employment

Indicators:

- Employed population
- Unemployment rate

Main question:

> Are more people working and has unemployment decreased over time?

---

### 3. Job Quality

Indicators:

- Permanent employees
- Temporary employees
- Full-time employment
- Part-time employment

Main question:

> Has employment growth also been accompanied by more stable and full-time jobs?

Fixed-discontinuous contracts are not analysed separately.

They are already included within permanent employment in the EPA data, and separating them consistently would require EPA microdata or a different methodology based on SEPE registered contracts.

The project will therefore analyse **permanent employment as a whole** without assuming that all permanent employment is continuous throughout the entire year.

---

### 4. Purchasing Power

Indicators:

- Salary
- Consumer Price Index (CPI)
- Real salary
- Purchasing power

Main question:

> Even if salaries have increased in nominal terms, can workers actually buy more than before?

---

## Study Period

The project analyses the period:

**2015–2026**

Special attention will also be given to:

- **2015** as the starting point of the analysis
- **2019** as the last complete pre-COVID year
- **2020** as an exceptional pandemic year
- **2021–2022** as the recovery and high-inflation period
- **2023–2025** as the most recent complete period
- **2026** as a partial year using the latest available data

The complete time series will be analysed instead of drawing conclusions from only two isolated years.

---

## Data Source

The main source is official public data from the:

**Instituto Nacional de Estadística (INE)**

The data will be retrieved directly through the official INE JSON API.

Official API documentation:

https://www.ine.es/dyngs/DAB/index.htm?cid=1099

---

## INE Data Hierarchy

The INE data was explored using the following hierarchy:

```text
Category
   ↓
Operation
   ↓
Table
   ↓
Series
   ↓
Observations
```

### Operation

A specific statistical study.

Examples:

- Encuesta de Población Activa
- Índice de Precios de Consumo
- Encuesta Trimestral de Coste Laboral

### Table

A collection of related statistical series inside an operation.

### Series

A specific indicator measured over time.

Example:

```text
EPA400155
→ Permanent salaried employees
```

### Observation

The value of a series for a particular period.

Example:

```text
2015 Q1 → 10997.3
```

If the EPA scale is expressed in thousands:

```text
10997.3
=
10,997,300 persons
≈
11 million persons
```

---

## API Exploration Strategy

During the exploration phase, complete tables were queried because the exact series codes were not yet known.

Example:

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/65132?date=20150101:20261231&tip=A
```

Once the correct series were identified, the production pipeline can query each series directly.

Production pattern:

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/{SERIES_CODE}?date=20150101:20261231&tip=A
```

This avoids downloading every series contained in a table when only one specific indicator is needed.

---

## Main API Endpoints

### Available Operations

```text
https://servicios.ine.es/wstempus/js/ES/OPERACIONES_DISPONIBLES
```

Used to discover statistical operations and their `Cod_IOE`.

---

### Tables of an Operation

```text
https://servicios.ine.es/wstempus/js/ES/TABLAS_OPERACION/{IOE}?det=2&tip=A
```

Example:

```text
https://servicios.ine.es/wstempus/js/ES/TABLAS_OPERACION/IOE30138?det=2&tip=A
```

Used to discover the tables contained inside an operation.

---

### Data from a Table

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/{TABLE_ID}?date=20150101:20261231&tip=A
```

Used mainly during exploration.

---

### Data from a Series

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/{SERIES_CODE}?date=20150101:20261231&tip=A
```

This will be the preferred production endpoint.

---

## INE Series

| Indicator | Operation | Table | Series | Unit | Frequency |
|---|---|---|---|---|---|
| Real GDP | `IOE30024` | `67822` | `CNTR6652` | Index | Quarterly |
| Population | `IOE30282` | `56934` + `59583` | `ECP320` | Persons | Historical / Quarterly |
| Employed population | `IOE30308` | `65109` | `EPA387796` | Thousands of persons | Quarterly |
| Unemployment rate | `IOE30308` | `65219` | `EPA423474` | % | Quarterly |
| Permanent employees | `IOE30308` | `65132` | `EPA400155` | Thousands of persons | Quarterly |
| Temporary employees | `IOE30308` | `65132` | `EPA400159` | Thousands of persons | Quarterly |
| Full-time employment | `IOE30308` | `65148` | `EPA404360` | Thousands of persons | Quarterly |
| Part-time employment | `IOE30308` | `65148` | `EPA404362` | Thousands of persons | Quarterly |
| Salary | `IOE30187` | `6038` | `ETCL1527` | Euros | Quarterly |
| CPI | `IOE30138` | `24077` | `IPC290751` | Index, base 2025 = 100 | Monthly |

---

## Series Configuration

The project will store the official INE series codes using readable internal aliases.

Example:

```python
SERIES = {
    "gdp_real": "CNTR6652",
    "population": "ECP320",
    "employed": "EPA387796",
    "unemployment_rate": "EPA423474",
    "indefinite": "EPA400155",
    "temporary": "EPA400159",
    "full_time": "EPA404360",
    "part_time": "EPA404362",
    "salary": "ETCL1527",
    "cpi": "IPC290751",
}
```

The aliases are internal project names.

For example:

```text
gdp_real
```

is only a readable name used by the project.

The INE identifies that series through:

```text
CNTR6652
```

The dictionary also allows the extraction process to iterate through all series automatically instead of writing each request manually.

---

## Reference URLs

### Real GDP

Table:

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/67822?date=20150101:20261231&tip=A
```

Series:

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/CNTR6652?date=20150101:20261231&tip=A
```

---

### Population

Historical table:

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/56934?date=20150101:20250331&tip=A
```

Recent continuation:

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/59583?date=20250401:20261231&tip=A
```

Series code:

```text
ECP320
```

Before closing the final extractor, it must be verified whether:

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/ECP320?date=20150101:20261231&tip=A
```

returns the complete period continuously.

If not, the two population tables will be extracted separately and concatenated.

---

### Employed Population

Table:

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/65109?date=20150101:20261231&tip=A
```

Series:

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/EPA387796?date=20150101:20261231&tip=A
```

---

### Unemployment Rate

Table:

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/65219?date=20150101:20261231&tip=A
```

Series:

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/EPA423474?date=20150101:20261231&tip=A
```

---

### Permanent and Temporary Employees

Table:

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/65132?date=20150101:20261231&tip=A
```

Permanent employees:

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/EPA400155?date=20150101:20261231&tip=A
```

Temporary employees:

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/EPA400159?date=20150101:20261231&tip=A
```

---

### Full-Time and Part-Time Employment

Table:

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/65148?date=20150101:20261231&tip=A
```

Full-time:

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/EPA404360?date=20150101:20261231&tip=A
```

Part-time:

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/EPA404362?date=20150101:20261231&tip=A
```

---

### Salary

Table:

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/6038?date=20150101:20261231&tip=A
```

Series:

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/ETCL1527?date=20150101:20261231&tip=A
```

---

### CPI

Table:

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/24077?date=20150101:20261231&tip=A
```

Series:

```text
https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/IPC290751?date=20150101:20261231&tip=A
```

---

## Important Methodological Decisions

### Real GDP Instead of Nominal GDP

The project uses real GDP because nominal GDP can increase simply because prices have increased.

The selected series:

```text
CNTR6652
```

represents GDP at market prices using chain-linked volume indices adjusted for seasonality and calendar effects.

The objective is to analyse changes in actual production rather than changes caused only by prices.

---

## Real GDP Per Capita

The GDP series used in the project is an **index**, not GDP expressed directly in euros.

Therefore, this would be incorrect:

```text
GDP index / population
=
GDP per capita in euros
```

The result would not represent euros per inhabitant.

Instead, the project will construct a relative real GDP per capita index.

Conceptually:

```text
Real GDP growth
        ↓
compared with
        ↓
Population growth
        ↓
Real GDP per capita index
```

A possible methodology is:

```text
GDP_per_capita_index_t
=
(
    GDP_real_index_t / GDP_real_index_base
)
/
(
    Population_t / Population_base
)
× 100
```

The final base period and the treatment of missing historical quarterly population observations must still be validated before implementation.

---

## Labour Market Methodology

Permanent and temporary employment refer to **salaried workers**.

Full-time and part-time employment refer to **all employed workers**.

Therefore, their denominators must remain separate.

### Permanent Employment Percentage

```text
Permanent %
=
Permanent
/
(Permanent + Temporary)
× 100
```

### Temporary Employment Percentage

```text
Temporary %
=
Temporary
/
(Permanent + Temporary)
× 100
```

### Full-Time Employment Percentage

```text
Full-time %
=
Full-time
/
(Full-time + Part-time)
× 100
```

### Part-Time Employment Percentage

```text
Part-time %
=
Part-time
/
(Full-time + Part-time)
× 100
```

The two groups must not be mixed because they represent different populations.

---

## Fixed-Discontinuous Contracts

Fixed-discontinuous contracts were investigated but removed from the main project scope.

The EPA considers them part of permanent employment.

Conceptually:

```text
Permanent employees
│
├── Continuous permanent employees
└── Fixed-discontinuous employees
```

Therefore, the project does not lose those workers by excluding a separate fixed-discontinuous indicator.

They remain included inside:

```text
EPA400155
```

The project will simply avoid claiming that all permanent employees work continuously throughout the full year.

---

## SEPE Exploration

SEPE data was briefly investigated as a possible source for fixed-discontinuous contracts.

Historical Excel files contained registered contract statistics, including the category:

```text
FIJOS DISCONTINUOS
```

However, SEPE registered contracts represent a different concept from EPA employed persons.

Conceptually:

```text
EPA
→ people currently employed
→ stock

SEPE
→ contracts registered
→ flow
```

One worker can potentially generate more than one registered contract.

Using SEPE for only one indicator would therefore add:

- another methodology
- historical XLS processing
- additional extraction logic
- potential comparability problems
- significant complexity for limited analytical benefit

SEPE was therefore removed from the main pipeline.

---

## Salary

The selected salary series is:

```text
ETCL1527
```

It represents:

```text
Total National
Both working-time types
Industry + Construction + Services
Total salary cost
Euros
```

The project intentionally uses **salary cost** rather than total labour cost.

Total labour cost would also include employer contributions and other costs that do not represent salary received by the worker.

---

## CPI

The selected CPI series is:

```text
IPC290751
```

It represents:

```text
National
General Index
Index
Base 2025 = 100
```

The CPI value itself is **not an inflation percentage**.

Example:

```text
CPI = 103
```

does not mean:

```text
103% inflation
```

It means that the price level is approximately:

```text
3% above the base level 100
```

The index is more useful than storing only an inflation rate because it allows comparisons between any two periods and can be used to deflate nominal salary values.

---

## CPI Monthly to Quarterly Transformation

Most project indicators are quarterly.

The CPI is monthly.

To align the CPI with quarterly salary data, a quarterly arithmetic average will be calculated.

```text
Q1 = average(January, February, March)

Q2 = average(April, May, June)

Q3 = average(July, August, September)

Q4 = average(October, November, December)
```

Example:

```text
January CPI  = 100
February CPI = 101
March CPI    = 102

Q1 CPI
=
(100 + 101 + 102) / 3
=
101
```

This transformation allows salary and CPI data to share the same quarterly frequency.

---

## Real Salary and Purchasing Power

Nominal salary alone does not indicate whether workers can actually buy more goods and services.

A salary can increase while prices increase even faster.

Using CPI base 2025 = 100:

```text
Real salary
=
Nominal salary × 100 / Quarterly CPI
```

This expresses salary approximately in constant 2025-price terms.

Interpretation:

```text
Nominal salary ↑
CPI ↑ faster
        ↓
Real salary ↓
```

The result will be used as an approximation of salary purchasing power.

It should not be interpreted as a complete measure of citizen welfare.

---

## Extraction Strategy

The project will not make one API request for every month or quarter.

Each series request retrieves all observations available inside the requested date range.

Conceptually:

```text
1 series
   ↓
1 API request
   ↓
all observations from 2015 to 2026
```

The project currently requires approximately:

```text
10 main INE series
≈
10 API requests per extraction run
```

This is significantly cleaner than repeatedly querying full tables.

---

## Extraction Configuration

Example configuration:

```python
SERIES = {
    "gdp_real": "CNTR6652",
    "population": "ECP320",
    "employed": "EPA387796",
    "unemployment_rate": "EPA423474",
    "indefinite": "EPA400155",
    "temporary": "EPA400159",
    "full_time": "EPA404360",
    "part_time": "EPA404362",
    "salary": "ETCL1527",
    "cpi": "IPC290751",
}
```

A future extraction process can iterate through this dictionary:

```python
for name, code in SERIES.items():
    ...
```

Conceptually:

```text
name = "gdp_real"
code = "CNTR6652"
```

Then:

```text
name = "population"
code = "ECP320"
```

and so on.

---

## Planned Extraction Pattern

```python
import requests

BASE_URL = "https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE"

SERIES = {
    "gdp_real": "CNTR6652",
    "population": "ECP320",
    "employed": "EPA387796",
    "unemployment_rate": "EPA423474",
    "indefinite": "EPA400155",
    "temporary": "EPA400159",
    "full_time": "EPA404360",
    "part_time": "EPA404362",
    "salary": "ETCL1527",
    "cpi": "IPC290751",
}


def get_series(series_code):
    url = f"{BASE_URL}/{series_code}"

    params = {
        "date": "20150101:20261231",
        "tip": "A",
    }

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()
```

The first implementation will initially test only one series before generalising the extractor.

---

## Data Engineering Architecture

The planned architecture is:

```text
INE API
   |
   v
Python Extraction
   |
   v
Apache Airflow
   |
   v
Bronze Layer
Raw JSON
   |
   v
Databricks
   |
   v
Apache Spark / PySpark
   |
   +--> Schema normalization
   +--> Date transformations
   +--> Unit normalization
   +--> CPI monthly → quarterly
   +--> Labour market percentages
   +--> Real salary
   +--> Real GDP per capita index
   |
   v
Silver Layer
   |
   v
Gold Layer
   |
   v
Power BI
   |
   v
Economic Analysis
   |
   v
Final Conclusions
```

---

## Data Layers

### Bronze Layer

Contains raw data exactly as returned by the source.

Example:

```text
INE API
   ↓
JSON
   ↓
data/bronze/
```

No economic transformations should be applied in Bronze.

The original source structure should be preserved whenever possible.

---

### Silver Layer

Contains cleaned and standardized data.

Expected transformations include:

- Normalizing dates
- Creating year and quarter fields
- Standardizing schemas
- Handling data types
- Converting thousands of persons when required
- Converting monthly CPI to quarterly CPI
- Validating missing observations
- Preparing datasets for joins

Example:

```text
Raw EPA JSON
   ↓
Clean schema
   ↓
year
quarter
value
indicator
```

---

### Gold Layer

Contains analysis-ready datasets and derived indicators.

Possible Gold datasets include:

- Real GDP evolution
- Real GDP per capita index
- Employment evolution
- Unemployment evolution
- Permanent vs temporary employment
- Full-time vs part-time employment
- Salary evolution
- Real salary
- Purchasing power evolution

These datasets will be prepared for Power BI and final analysis.

---

## Technology Stack

### Programming

- Python 3.12

### Data Extraction

- Requests
- INE JSON API

### Data Exploration and Validation

- Pandas
- Jupyter / IPython Kernel

### Testing

- Pytest

### Orchestration

- Apache Airflow

### Containers

- Docker

### Data Platform

- Databricks

### Distributed Processing

- Apache Spark
- PySpark

### Visualization

- Power BI

### Development Tools

- Conda
- VS Code
- Git
- GitHub

---

## Local Development Environment

A dedicated Conda environment has been created for the project.

```text
Environment name: economia
Python version: 3.12.13
```

Initial dependencies installed:

```text
requests
pandas
pytest
ipykernel
```

The environment is isolated from the other local Conda environments.

Current known Conda environments include:

```text
base
py314
economia
```

The `economia` environment is the one used for this project.

---

## VS Code Environment

VS Code is configured to use the Conda environment:

```text
economia
```

Interpreter:

```text
Python 3.12.13
```

The project also contains:

```text
.vscode/settings.json
```

which stores project-specific VS Code environment preferences.

The environment itself is not stored inside `.vscode`.

The real Conda environment exists externally in the local Anaconda installation.

Conceptually:

```text
Conda environment
C:\Users\Johan\anaconda3\envs\economia
        ↓
Python + installed packages


Project folder
spain-economy-data-engineering/
        ↓
.vscode/
        ↓
VS Code project configuration
```

---

## Airflow Strategy

Apache Airflow will **not** be installed directly inside the `economia` Conda environment.

It will be added later using Docker.

Planned architecture:

```text
Windows
│
├── VS Code
│
├── Conda
│   └── economia
│       └── Python extraction code
│
└── Docker Desktop
    └── Airflow containers
```

This keeps orchestration infrastructure isolated from the local Python development environment.

Airflow will be introduced only after the basic INE extractor works correctly.

---

## Project Structure

```text
spain-economy-data-engineering/
│
├── .vscode/
│
├── config/
│
├── src/
│   ├── extraction/
│   ├── transformations/
│   └── utils/
│
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── airflow/
│   └── dags/
│
├── databricks/
│   └── notebooks/
│
├── tests/
│
├── docs/
│
├── .gitignore
└── README.md
```

---

## Folder Responsibilities

### `config/`

Configuration shared by the project.

Planned contents:

```text
series.py
```

This will contain the INE series dictionary and other extraction configuration.

---

### `src/extraction/`

Code responsible for extracting source data.

Example future file:

```text
ine_client.py
```

Responsibilities:

- Build INE API requests
- Validate HTTP responses
- Retrieve JSON data
- Save raw data

---

### `src/transformations/`

Transformation logic.

Examples:

- CPI monthly to quarterly
- Labour market percentages
- Real salary
- Real GDP per capita index

---

### `src/utils/`

Reusable utility functions that do not belong directly to extraction or transformation logic.

---

### `data/bronze/`

Raw source data.

```text
INE API JSON
```

---

### `data/silver/`

Cleaned and standardized datasets.

---

### `data/gold/`

Final analysis-ready datasets.

---

### `airflow/dags/`

Future Airflow DAG definitions.

---

### `databricks/notebooks/`

Databricks notebooks used for Spark / PySpark transformations and analysis.

---

### `tests/`

Automated tests using Pytest.

---

### `docs/`

Project documentation and context documents.

---

## Git Strategy

Git has already been initialized in the project root.

Generated datasets and local files that do not belong in the repository will be excluded through `.gitignore`.

Git does not track empty folders.

Therefore, some project directories may not appear in GitHub until they contain actual files.

This is expected and does not affect the local project structure.

---

## Current Project Status

### Research and Data Selection

- [x] Main project question defined
- [x] Study period defined
- [x] Economic analysis blocks defined
- [x] Official INE source selected
- [x] INE API hierarchy understood
- [x] Relevant INE operations identified
- [x] Relevant INE tables identified
- [x] Final main series identified
- [x] Real GDP series selected
- [x] Population series selected
- [x] Employed population selected
- [x] Unemployment rate selected
- [x] Permanent employees selected
- [x] Temporary employees selected
- [x] Full-time employment selected
- [x] Part-time employment selected
- [x] Salary series selected
- [x] CPI series selected

---

### Methodology

- [x] Nominal GDP rejected in favour of real GDP
- [x] CPI index interpretation understood
- [x] CPI monthly → quarterly methodology selected
- [x] Real salary methodology defined
- [x] Labour market percentage denominators defined
- [x] Fixed-discontinuous contracts removed from separate analysis
- [x] SEPE removed from the main pipeline
- [ ] Final real GDP per capita index implementation
- [ ] Population historical frequency treatment

---

### Development Environment

- [x] Git repository initialized
- [x] Dedicated Conda environment created
- [x] Environment named `economia`
- [x] Python 3.12.13 installed
- [x] Requests installed
- [x] Pandas installed
- [x] Pytest installed
- [x] IPython Kernel installed
- [x] VS Code configured with the `economia` environment
- [x] Project folder structure created
- [ ] `.gitignore` completed
- [ ] INE series configuration created
- [ ] First extractor implemented

---

## Next Steps

The next development steps are:

```text
1. Finish .gitignore
        ↓
2. Create config/series.py
        ↓
3. Implement one test INE request
        ↓
4. Save one raw JSON file in Bronze
        ↓
5. Generalize extraction for all series
        ↓
6. Validate population extraction
        ↓
7. Add tests
        ↓
8. Implement transformations
        ↓
9. Add Docker
        ↓
10. Add Airflow
        ↓
11. Connect Databricks
        ↓
12. Transform data with PySpark
        ↓
13. Build Silver and Gold datasets
        ↓
14. Connect Power BI
        ↓
15. Analyse results
        ↓
16. Write final conclusions
```

---

## Project Principle

This project does **not** attempt to prove a predefined political or economic conclusion.

The objective is to use official data to determine whether improvements in aggregate Spanish economic indicators have also translated into improvements for the average citizen.

The analysis must therefore distinguish between concepts such as:

```text
More GDP
≠
Automatically better living standards
```

```text
More employment
≠
Automatically better employment
```

```text
Higher nominal salary
≠
Automatically higher purchasing power
```

The conclusions must follow the data, even if the results contradict the initial expectations.

---

## Final Goal

The project should ultimately be able to answer four questions with data:

```text
1. Is Spain producing more?

2. Are more people working?

3. Are those jobs better?

4. Can workers actually buy more?
```

These answers will then be combined to address the main question:

> **Has the Spanish economy really improved for the average citizen between 2015 and 2026?**

---

## Status

🚧 **Project in development**

Current phase:

**Local environment and project structure setup before implementing the INE extraction pipeline.**