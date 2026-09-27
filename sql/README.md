# SQLite database

`ontario_enso.db` holds one pipeline run: every cleaned table, result, chart data table and
quality table, in a single file. Nothing needs installing to build it (Python's built-in
`sqlite3`), and anyone can open it.

| File | Purpose | Runs |
|---|---|---|
| `ontario_enso.db` | The database (about 14 MB) | |
| `schema.sql` | The empty tables, their keys and links, and the core views | 1st, by the loader |
| `winter_summary.sql` | The winter summary calculated in SQL, saved as `result_winter_summary_sql` (Definition of Done) | 2nd, by the loader |
| `dashboard_views.sql` | One ready-made view per dashboard page, plus metric labels (`dim_metric`) | 3rd, by the loader |
| `queries/` | Questions answered in SQL, one file per business question. They only read. | By you |
| `../python/05_database/load_database.py` | Builds the database from a pipeline run | |
| `../python/05_database/check_winter_summary.py` | Confirms the SQL winter summary matches pandas | |

### Query files

| File | Answers | Business questions |
|---|---|---|
| `queries/temperature_el_nino_vs_neutral.sql` | Were El Niño and strong El Niño winters warmer? Also ENSO strength vs temperature (S3), the trend check (S2) and warming trends (S1) | BQ1, BQ6 |
| `queries/snowfall_and_snow_days_el_nino_vs_neutral.sql` | Less snow and fewer snow days? Plus which stations' snow data is limited | BQ2, BQ5 |
| `queries/very_cold_days_el_nino_vs_neutral.sql` | Fewer days at −20 °C or colder? Plus the coldest El Niño winters and daily detail | BQ3 |
| `queries/south_vs_north_differences.sql` | How the differences change from south to north, and the Thunder Bay vs south test (S4) | BQ4 |
| `queries/impacts_heating_maple_growing_season_gdp.sql` | Heating demand, maple and freeze-thaw days, growing season, GDP (C5–C9) | BQ7–BQ10 |
| `queries/data_quality_and_coverage.sql` | Usable and excluded winters, baselines, ENSO class counts, which run is loaded | All |

## Tables (21) and views (8)

| Group | Tables | Contents |
|---|---|---|
| `dim_` (2) | `dim_city`, `dim_enso_winter` | Lookups: city name, region and latitude; ONI/RONI value and class for each winter. Other tables link to these. |
| `fact_` (6) | `fact_daily_weather`, `fact_winter_kpis`, `fact_sap_season`, `fact_growing_season`, `fact_maple_production`, `fact_ontario_gdp` | Measured data: 98,096 daily records, the winter KPIs (K1–K6 inputs), and the impact KPIs (K7–K10) |
| `result_` (11) | `result_enso_comparisons`, `result_trend_sensitivity`, `result_regional_comparisons`, `result_temperature_trends`, `result_city_baselines`, `result_winter_summary_sql` | Core results: El Niño/La Niña minus neutral with 95% intervals (C1–C4), the trend check (S2), north–south test (S4), warming trends (S1), 1991–2020 baselines, and the winter summary built in SQL |
| | `result_heating_demand`, `result_growing_season`, `result_maple_freeze_thaw`, `result_impact_tests`, `result_index_slopes` | Impact and supporting results: C5–C9 and S3 |
| `meta_` (1) | `meta_pipeline_runs` | Which pipeline run is loaded |
| (dashboard) | `dim_metric` | Display label, unit and KPI ID for each measure, created by `dashboard_views.sql` |

| View | Use |
|---|---|
| `v_winter_kpis` | Winter KPIs with city details and both ENSO labels |
| `v_enso_comparisons` | All comparison results with city details and latitude |
| `v_daily_weather` | Daily records with city name and the winter's ENSO class |
| `v_dash_map` | **Map page:** one row per station with location, usable winters and headline results |
| `v_dash_comparison` | **Comparison page:** every difference with its interval, display labels, and a result label (Clear difference / Borderline / Inconclusive) |
| `v_dash_group_averages` | Average winter by ENSO group, for cards and bar charts |
| `v_dash_timeline` | **Timeline page:** anomaly per winter with the station's trend line |
| `v_dash_impacts` | **Impacts page:** C5–C9 in one shape, with caveats in `note` |

"Borderline" marks results whose interval clears zero by less than 2% of the estimate's size
(Thunder Bay heating demand; London strong El Niño snowfall). Show them as uncertain.

KPI and comparison IDs (K1–K10, C1–C9, S1–S6) are defined in `docs/kpis_and_business_questions.md`.
City names and ENSO labels are stored once, in the `dim_` tables; the views join them in.
True/false columns are 1/0, missing values are NULL (never zero), and dates are text in
`YYYY-MM-DD` form. `docs/data_dictionary.md` defines every column.

Every chart in the report can be rebuilt from these tables. The pipeline's per-chart CSVs
(`runs/<timestamp>/data/chart_data/`) and data-quality audit files (`runs/<timestamp>/reports/`)
stay as files and are not loaded.

## Build or rebuild

Run the pipeline first (`python python/run_pipeline.py`), then from the repository folder:

```bash
python python/05_database/load_database.py            # loads the latest run in runs/
python python/05_database/check_winter_summary.py     # SQL vs pandas check
```

Each load rebuilds every table, so the database always matches exactly one run. To load an
older run: `--run runs/<timestamp>`. Close any program that has the database open first.

## Check

`check_winter_summary.py` compares all 240 rows of `result_winter_summary_sql` (built in SQL
from `fact_winter_kpis`) with pandas' `data/enso_group_summary.csv` from the same run
(6 cities × 2 indices × 4 ENSO groups × 5 KPIs): winter counts and eligible winters must be
equal, and mean, median, standard deviation, min and max must agree to 10 significant digits
(the precision of the pipeline's CSVs). Expected output:

```
SQL winter summary matches pandas: 240 rows (6 cities x 2 indices x 4 ENSO groups x 5 KPIs), counts and winters equal, statistics equal to 10 significant digits.
```

## Open the database

[DB Browser for SQLite](https://sqlitebrowser.org/) (free) opens `ontario_enso.db` directly:
browse any table in *Browse Data*, or open any file from `queries/` in *Execute SQL* and run it.

## Power BI

Power BI has no built-in SQLite connector; it reads SQLite through ODBC. One-time setup:

1. Install a SQLite ODBC driver for Windows, 64-bit to match Power BI Desktop. A widely used free
   option is the SQLite ODBC Driver by Christian Werner (`sqliteodbc_w64.exe`).
2. In Power BI Desktop: **Get Data → ODBC**. Choose *(None)* for the data source name, open
   *Advanced options*, and enter this connection string with your own path:
   ```
   Driver={SQLite3 ODBC Driver};Database=C:\path\to\ontario-elnino-winters\sql\ontario_enso.db;
   ```
   The driver name must match the one listed in Windows' **ODBC Data Sources (64-bit)** → *Drivers*.
3. Select the tables or views to import.

Import the `v_dash_` views: each one is shaped for a dashboard page, with display labels
and sort columns (`south_to_north`, `group_order`, `metric_order`) for ordering axes. The map
page's `map_location` column (for example "Thunder Bay, Ontario, Canada") works in the Map
visual's *Location* field. For your own model instead, relate the `fact_` and `result_` tables
to `dim_city` on `city`, and `fact_winter_kpis` to `dim_enso_winter` on `winter_year`.
True/false columns arrive as 1/0. Dates arrive as text: set the column type to *Date* in Power Query.
Refresh in Power BI after rebuilding the database.
