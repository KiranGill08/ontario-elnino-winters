-- Ontario Winters and El Nino: SQLite schema
--
-- Rebuilt on every load by python/05_database/load_database.py, which then fills the
-- tables from one pipeline run (runs/<timestamp>/) into sql/ontario_enso.db. Table groups:
--   dim_     lookups other tables join to (cities, ENSO label per winter)
--   fact_    measured data (daily weather, winter and season KPIs, maple, GDP)
--   result_  statistical results: El Nino comparisons, trends, the SQL winter summary
--            and the impact results (heating, growing season, maple, tests, slopes)
--   meta_    which run is loaded
--   v_       views that add city names and ENSO labels
-- Built afterwards: result_winter_summary_sql (winter_summary.sql) and the
-- dashboard views v_dash_* with dim_metric (dashboard_views.sql).
-- Column names match the pipeline's CSVs; docs/data_dictionary.md defines them.
-- True/false columns are INTEGER 1/0; missing values are NULL, never zero;
-- dates are TEXT in YYYY-MM-DD form.

PRAGMA foreign_keys = OFF;
DROP VIEW IF EXISTS v_winter_kpis;
DROP VIEW IF EXISTS v_enso_comparisons;
DROP VIEW IF EXISTS v_daily_weather;
DROP VIEW IF EXISTS v_temperature_timeline;
DROP VIEW IF EXISTS v_dash_map;
DROP VIEW IF EXISTS v_dash_comparison;
DROP VIEW IF EXISTS v_dash_group_averages;
DROP VIEW IF EXISTS v_dash_timeline;
DROP VIEW IF EXISTS v_dash_impacts;
DROP TABLE IF EXISTS dim_metric;
DROP TABLE IF EXISTS meta_pipeline_runs;
DROP TABLE IF EXISTS result_winter_summary_sql;
DROP TABLE IF EXISTS result_index_slopes;
DROP TABLE IF EXISTS result_impact_tests;
DROP TABLE IF EXISTS result_maple_freeze_thaw;
DROP TABLE IF EXISTS result_growing_season;
DROP TABLE IF EXISTS result_heating_demand;
DROP TABLE IF EXISTS result_regional_comparisons;
DROP TABLE IF EXISTS result_trend_sensitivity;
DROP TABLE IF EXISTS result_enso_comparisons;
DROP TABLE IF EXISTS result_temperature_trends;
DROP TABLE IF EXISTS result_city_baselines;
DROP TABLE IF EXISTS fact_ontario_gdp;
DROP TABLE IF EXISTS fact_maple_production;
DROP TABLE IF EXISTS fact_growing_season;
DROP TABLE IF EXISTS fact_sap_season;
DROP TABLE IF EXISTS fact_winter_kpis;
DROP TABLE IF EXISTS fact_daily_weather;
DROP TABLE IF EXISTS dim_enso_winter;
DROP TABLE IF EXISTS dim_city;
PRAGMA foreign_keys = ON;

-- data/city_baselines.csv
CREATE TABLE dim_city (
  city TEXT NOT NULL,
  city_name TEXT,
  region TEXT,
  latitude_approx REAL,
  included_in_proposal INTEGER,
  included_in_repo_study INTEGER,
  PRIMARY KEY (city)
);

-- data/enso_winter_labels.csv
CREATE TABLE dim_enso_winter (
  winter_year INTEGER NOT NULL,
  oni_djf REAL,
  roni_djf REAL,
  enso_class_oni TEXT,
  strong_el_nino_oni INTEGER,
  enso_class_roni TEXT,
  strong_el_nino_roni INTEGER,
  PRIMARY KEY (winter_year)
);

-- data/all_stations_daily_enriched.csv
CREATE TABLE fact_daily_weather (
  city TEXT NOT NULL,
  source_file TEXT,
  source_row INTEGER,
  date TEXT NOT NULL,
  station_id INTEGER,
  tmax REAL,
  tmin REAL,
  tmean REAL,
  rain_mm REAL,
  snowfall_cm REAL,
  precip_mm REAL,
  tmean_analysis REAL,
  tmean_derived INTEGER,
  quality_notes TEXT,
  winter_year INTEGER,
  year INTEGER,
  month INTEGER,
  is_winter INTEGER,
  in_study_period INTEGER,
  snow_day REAL,
  very_cold_day REAL,
  PRIMARY KEY (city, date),
  FOREIGN KEY (city) REFERENCES dim_city (city)
);

-- data/winter_kpis.csv
CREATE TABLE fact_winter_kpis (
  city TEXT NOT NULL,
  winter_year INTEGER NOT NULL,
  expected_days INTEGER,
  recorded_days INTEGER,
  missing_calendar_days INTEGER,
  valid_temperature_days INTEGER,
  valid_snowfall_days INTEGER,
  derived_temperature_days INTEGER,
  temperature_pass INTEGER,
  snowfall_pass INTEGER,
  cold_days_pass INTEGER,
  mean_temp REAL,
  snowfall_total_cm REAL,
  snow_days REAL,
  days_below_m20 REAL,
  exclusion_reasons TEXT,
  baseline_mean_temp REAL,
  baseline_n_winters INTEGER,
  baseline_start_winter INTEGER,
  baseline_end_winter INTEGER,
  baseline_complete INTEGER,
  baseline_status TEXT,
  temp_anomaly REAL,
  winter_label TEXT,
  winter_start TEXT,
  winter_end TEXT,
  temperature_coverage_pct REAL,
  snowfall_coverage_pct REAL,
  derived_temperature_share_pct REAL,
  quality_method TEXT,
  temp_detrended_residual REAL,
  PRIMARY KEY (city, winter_year),
  FOREIGN KEY (city) REFERENCES dim_city (city),
  FOREIGN KEY (winter_year) REFERENCES dim_enso_winter (winter_year)
);

-- data/sap_season_kpis.csv
CREATE TABLE fact_sap_season (
  city TEXT NOT NULL,
  year INTEGER NOT NULL,
  expected_days INTEGER,
  recorded_days INTEGER,
  missing_calendar_days INTEGER,
  valid_temperature_days INTEGER,
  temperature_pass INTEGER,
  snowfall_pass INTEGER,
  cold_days_pass INTEGER,
  freeze_thaw_pass INTEGER,
  mean_temp REAL,
  snowfall_total_cm REAL,
  snow_days REAL,
  days_below_m20 REAL,
  freeze_thaw_days REAL,
  baseline_mean_temp REAL,
  temp_anomaly REAL,
  PRIMARY KEY (city, year),
  FOREIGN KEY (city) REFERENCES dim_city (city),
  FOREIGN KEY (year) REFERENCES dim_enso_winter (winter_year)
);

-- data/growing_season_kpis.csv
CREATE TABLE fact_growing_season (
  city TEXT NOT NULL,
  year INTEGER NOT NULL,
  last_spring_frost TEXT,
  first_fall_frost TEXT,
  growing_season_days REAL,
  n_valid_tmin_days INTEGER,
  complete INTEGER,
  PRIMARY KEY (city, year),
  FOREIGN KEY (city) REFERENCES dim_city (city),
  FOREIGN KEY (year) REFERENCES dim_enso_winter (winter_year)
);

-- data/ontario_maple_syrup_production.csv
CREATE TABLE fact_maple_production (
  year INTEGER NOT NULL,
  syrup_thousand_gallons INTEGER,
  gross_value_thousand_cad INTEGER,
  quality_notes TEXT,
  PRIMARY KEY (year)
);

-- data/ontario_gdp.csv
CREATE TABLE fact_ontario_gdp (
  year INTEGER NOT NULL,
  gdp_chained_2017_millions INTEGER,
  gdp_growth_pct REAL,
  quality_notes TEXT,
  PRIMARY KEY (year)
);

-- data/city_baselines.csv
CREATE TABLE result_city_baselines (
  city TEXT NOT NULL,
  baseline_mean_temp REAL,
  baseline_n_winters INTEGER,
  baseline_start_winter INTEGER,
  baseline_end_winter INTEGER,
  baseline_complete INTEGER,
  baseline_status TEXT,
  PRIMARY KEY (city),
  FOREIGN KEY (city) REFERENCES dim_city (city)
);

-- data/temperature_trends.csv
CREATE TABLE result_temperature_trends (
  city TEXT NOT NULL,
  n_winters INTEGER,
  slope_c_per_decade REAL,
  intercept REAL,
  first_winter INTEGER,
  last_winter INTEGER,
  PRIMARY KEY (city),
  FOREIGN KEY (city) REFERENCES dim_city (city)
);

-- data/enso_comparisons.csv
CREATE TABLE result_enso_comparisons (
  city TEXT NOT NULL,
  enso_index TEXT NOT NULL,
  metric TEXT NOT NULL,
  comparison_group TEXT NOT NULL,
  reference_group TEXT NOT NULL,
  comparison_mean REAL,
  reference_mean REAL,
  difference REAL,
  ci_lower REAL,
  ci_upper REAL,
  status TEXT,
  n_comparison INTEGER,
  n_reference INTEGER,
  comparison_years TEXT,
  reference_years TEXT,
  bootstrap_samples INTEGER,
  sample_note TEXT,
  quality_method TEXT,
  PRIMARY KEY (city, enso_index, metric, comparison_group, reference_group),
  FOREIGN KEY (city) REFERENCES dim_city (city)
);

-- data/temperature_trend_sensitivity.csv
CREATE TABLE result_trend_sensitivity (
  city TEXT NOT NULL,
  enso_index TEXT NOT NULL,
  metric TEXT NOT NULL,
  comparison_group TEXT NOT NULL,
  reference_group TEXT NOT NULL,
  comparison_mean REAL,
  reference_mean REAL,
  difference REAL,
  ci_lower REAL,
  ci_upper REAL,
  status TEXT,
  n_comparison INTEGER,
  n_reference INTEGER,
  comparison_years TEXT,
  reference_years TEXT,
  bootstrap_samples INTEGER,
  sample_note TEXT,
  quality_method TEXT,
  PRIMARY KEY (city, enso_index, metric, comparison_group, reference_group),
  FOREIGN KEY (city) REFERENCES dim_city (city)
);

-- data/regional_comparisons.csv
CREATE TABLE result_regional_comparisons (
  north_city TEXT NOT NULL,
  south_city TEXT NOT NULL,
  enso_index TEXT NOT NULL,
  metric TEXT NOT NULL,
  difference_of_differences REAL,
  ci_lower REAL,
  ci_upper REAL,
  status TEXT,
  n_common_el_nino INTEGER,
  n_common_neutral INTEGER,
  el_nino_years TEXT,
  neutral_years TEXT,
  PRIMARY KEY (north_city, south_city, enso_index, metric),
  FOREIGN KEY (north_city) REFERENCES dim_city (city),
  FOREIGN KEY (south_city) REFERENCES dim_city (city)
);

-- data/chart_data/eda_heating_demand_by_city.csv
CREATE TABLE result_heating_demand (
  city TEXT NOT NULL,
  n_el_nino INTEGER,
  n_neutral INTEGER,
  el_nino_mean_hdd REAL,
  neutral_mean_hdd REAL,
  diff_hdd REAL,
  ci_lower_hdd REAL,
  ci_upper_hdd REAL,
  pct REAL,
  pct_lo REAL,
  pct_hi REAL,
  status TEXT,
  PRIMARY KEY (city),
  FOREIGN KEY (city) REFERENCES dim_city (city)
);

-- data/chart_data/eda_growing_season_by_city.csv
CREATE TABLE result_growing_season (
  city TEXT NOT NULL,
  label TEXT,
  n_el_nino INTEGER,
  n_neutral INTEGER,
  diff_days REAL,
  ci_lower REAL,
  ci_upper REAL,
  status TEXT,
  PRIMARY KEY (city)
);

-- data/chart_data/eda_freeze_thaw_vs_maple.csv
CREATE TABLE result_maple_freeze_thaw (
  year INTEGER NOT NULL,
  syrup_thousand_gallons INTEGER,
  maple_trend REAL,
  maple_residual REAL,
  enso_class_oni TEXT,
  enso_class_roni TEXT,
  freeze_thaw_days REAL,
  fitted_residual REAL,
  PRIMARY KEY (year)
);

-- data/chart_impact_tests.csv
CREATE TABLE result_impact_tests (
  test TEXT NOT NULL,
  statistic TEXT,
  estimate REAL,
  ci_lower REAL,
  ci_upper REAL,
  status TEXT,
  n_comparison INTEGER,
  n_reference INTEGER,
  PRIMARY KEY (test)
);

-- data/chart_index_vs_anomaly_slopes.csv
CREATE TABLE result_index_slopes (
  city TEXT NOT NULL,
  enso_index TEXT NOT NULL,
  n_winters INTEGER,
  slope_c_per_index_unit REAL,
  intercept REAL,
  ci_lower REAL,
  ci_upper REAL,
  pearson_r REAL,
  PRIMARY KEY (city, enso_index),
  FOREIGN KEY (city) REFERENCES dim_city (city)
);

-- One row describing the run currently loaded
CREATE TABLE meta_pipeline_runs (
  run_id INTEGER PRIMARY KEY,
  run_folder TEXT NOT NULL,
  pipeline_completed_utc TEXT,
  loaded_utc TEXT,
  validation TEXT,
  daily_rows INTEGER,
  winter_rows INTEGER,
  manifest_json TEXT
);

-- ---------- Views ----------

-- Winter KPIs with city details and both ENSO labels
CREATE VIEW v_winter_kpis AS
SELECT w.*, c.city_name, c.region, c.latitude_approx,
       e.roni_djf, e.enso_class_roni, e.strong_el_nino_roni,
       e.oni_djf, e.enso_class_oni, e.strong_el_nino_oni
FROM fact_winter_kpis w
JOIN dim_city c ON c.city = w.city
JOIN dim_enso_winter e ON e.winter_year = w.winter_year;

-- El Nino / La Nina comparisons with city details
CREATE VIEW v_enso_comparisons AS
SELECT r.*, c.city_name, c.region, c.latitude_approx
FROM result_enso_comparisons r
JOIN dim_city c ON c.city = r.city;

-- Daily weather with city name and the winter's RONI class (NULL outside winter)
CREATE VIEW v_daily_weather AS
SELECT d.*, c.city_name, e.enso_class_roni, e.strong_el_nino_roni
FROM fact_daily_weather d
JOIN dim_city c ON c.city = d.city
LEFT JOIN dim_enso_winter e ON e.winter_year = d.winter_year AND d.is_winter = 1;

