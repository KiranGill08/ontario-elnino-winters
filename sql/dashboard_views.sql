-- Dashboard views: one ready-made view per Power BI page, plus metric labels.
-- Run by python/05_database/load_database.py after the data and the winter summary are loaded.
-- All views use RONI (the primary index) and compare against neutral winters.
-- Pages follow the dashboard plan in docs/kpis_and_business_questions.md, section 8.
--
--   v_dash_map             Station map: one row per station with its headline El Nino differences
--   v_dash_comparison      ENSO comparison: every difference with its 95% interval (C1-C4)
--   v_dash_group_averages  Average winter by ENSO group (cards, bar charts)
--   v_dash_timeline        Timeline: anomaly per winter with the station's trend line
--   v_dash_impacts         Impacts: heating, growing season, maple and GDP results (C5-C9)

-- ---------- Metric labels (static reference table) ----------
DROP TABLE IF EXISTS dim_metric;
CREATE TABLE dim_metric (
  metric TEXT PRIMARY KEY,
  kpi_id TEXT,
  label TEXT,                 -- display name for charts
  unit TEXT,
  milder_if TEXT,             -- which sign of El Nino minus neutral means a milder winter
  sort_order INTEGER
);
INSERT INTO dim_metric VALUES
  ('temp_anomaly',      'K2', 'Temperature anomaly',        '°C',   'positive', 1),
  ('snowfall_total_cm', 'K3', 'Total snowfall',             'cm',   'negative', 2),
  ('snow_days',         'K4', 'Snow days (1 cm or more)',   'days', 'negative', 3),
  ('days_below_m20',    'K5', 'Very cold days (-20 °C or colder)', 'days', 'negative', 4),
  ('mean_temp',         'K1', 'Mean winter temperature',    '°C',   'positive', 5);

-- ---------- Station map ----------
-- One row per station: where it is, how many usable winters, and its headline results.
-- map_location is a place name Power BI's map visual can locate.
DROP VIEW IF EXISTS v_dash_map;
CREATE VIEW v_dash_map AS
SELECT c.city, c.city_name, c.region, c.latitude_approx,
       c.city_name || ', Ontario, Canada' AS map_location,
       RANK() OVER (ORDER BY c.latitude_approx) AS south_to_north,
       (SELECT SUM(temperature_pass) FROM fact_winter_kpis w WHERE w.city = c.city) AS temperature_winters,
       (SELECT SUM(snowfall_pass) FROM fact_winter_kpis w WHERE w.city = c.city) AS snowfall_winters,
       MAX(CASE WHEN r.metric = 'temp_anomaly' AND r.comparison_group = 'El Nino' THEN r.difference END) AS el_nino_temp_diff_c,
       MAX(CASE WHEN r.metric = 'temp_anomaly' AND r.comparison_group = 'Strong El Nino' THEN r.difference END) AS strong_temp_diff_c,
       MAX(CASE WHEN r.metric = 'temp_anomaly' AND r.comparison_group = 'Strong El Nino'
                THEN r.status = 'interval_excludes_zero' END) AS strong_temp_significant,
       MAX(CASE WHEN r.metric = 'snow_days' AND r.comparison_group = 'El Nino' THEN r.difference END) AS el_nino_snow_days_diff,
       MAX(CASE WHEN r.metric = 'snow_days' AND r.comparison_group = 'El Nino'
                THEN r.status = 'interval_excludes_zero' END) AS el_nino_snow_days_significant
FROM dim_city c
LEFT JOIN result_enso_comparisons r
       ON r.city = c.city AND r.enso_index = 'RONI' AND r.reference_group = 'Neutral'
GROUP BY c.city;

-- ---------- ENSO comparison ----------
-- Every El Nino, Strong El Nino and La Nina minus neutral difference, with display labels.
DROP VIEW IF EXISTS v_dash_comparison;
CREATE VIEW v_dash_comparison AS
SELECT r.city, c.city_name, c.latitude_approx,
       RANK() OVER (PARTITION BY r.metric, r.comparison_group ORDER BY c.latitude_approx) AS south_to_north,
       r.metric, m.kpi_id, m.label AS metric_label, m.unit, m.sort_order AS metric_order,
       r.comparison_group,
       CASE r.comparison_group WHEN 'La Nina' THEN 1 WHEN 'El Nino' THEN 2 ELSE 3 END AS group_order,
       r.comparison_mean, r.reference_mean, r.difference, r.ci_lower, r.ci_upper,
       r.n_comparison, r.n_reference,
       r.status = 'interval_excludes_zero' AS is_significant,
       -- borderline: clears zero, but the nearer interval end is within 2% of the estimate's size from zero
       (r.status = 'interval_excludes_zero'
        AND MIN(ABS(r.ci_lower), ABS(r.ci_upper)) < 0.02 * ABS(r.difference)) AS is_borderline,
       CASE WHEN r.status <> 'interval_excludes_zero' THEN 'Inconclusive'
            WHEN MIN(ABS(r.ci_lower), ABS(r.ci_upper)) < 0.02 * ABS(r.difference) THEN 'Borderline'
            ELSE 'Clear difference' END AS result_label,
       r.comparison_years, r.reference_years
FROM result_enso_comparisons r
JOIN dim_city c ON c.city = r.city
JOIN dim_metric m ON m.metric = r.metric
WHERE r.enso_index = 'RONI' AND r.reference_group = 'Neutral' AND r.metric <> 'mean_temp';

-- ---------- Average winter by ENSO group ----------
DROP VIEW IF EXISTS v_dash_group_averages;
CREATE VIEW v_dash_group_averages AS
SELECT s.city, c.city_name, c.latitude_approx, s.metric, m.label AS metric_label, m.unit,
       m.sort_order AS metric_order, s.enso_group,
       CASE s.enso_group WHEN 'La Nina' THEN 1 WHEN 'Neutral' THEN 2 WHEN 'El Nino' THEN 3 ELSE 4 END AS group_order,
       s.n_eligible AS winters, s.mean, s.median, s.min, s.max
FROM result_winter_summary_sql s
JOIN dim_city c ON c.city = s.city
JOIN dim_metric m ON m.metric = s.metric
WHERE s.enso_index = 'RONI';

-- ---------- Timeline ----------
-- Anomaly per winter with the station's warming-trend line on the anomaly scale.
-- The trend is fitted to mean temperature, so the 1991-2020 baseline is subtracted.
DROP VIEW IF EXISTS v_dash_timeline;
CREATE VIEW v_dash_timeline AS
SELECT w.city, c.city_name, c.latitude_approx, w.winter_year, w.winter_label, w.temp_anomaly,
       e.roni_djf, e.enso_class_roni, e.strong_el_nino_roni,
       t.intercept + t.slope_c_per_decade / 10.0 * w.winter_year - b.baseline_mean_temp AS trend_fit,
       t.slope_c_per_decade,
       w.temp_anomaly IS NULL AS excluded
FROM fact_winter_kpis w
JOIN dim_city c ON c.city = w.city
JOIN dim_enso_winter e ON e.winter_year = w.winter_year
JOIN result_temperature_trends t ON t.city = w.city
JOIN result_city_baselines b ON b.city = w.city;

-- ---------- Impacts ----------
-- One row per impact result (C5-C9), in one shape so a single table or chart can show them.
-- city is 'province' for Ontario-wide results.
DROP VIEW IF EXISTS v_dash_impacts;
CREATE VIEW v_dash_impacts AS
SELECT 'C5' AS comparison_id, 'Heating demand, El Nino minus neutral' AS impact,
       h.city, c.city_name, h.pct AS estimate, h.pct_lo AS ci_lower, h.pct_hi AS ci_upper, '% of neutral' AS unit,
       h.status = 'interval_excludes_zero' AS is_significant, h.n_el_nino AS n_comparison, h.n_neutral AS n_reference,
       CASE WHEN h.status = 'interval_excludes_zero' AND MIN(ABS(h.pct_lo), ABS(h.pct_hi)) < 0.02 * ABS(h.pct)
            THEN 'Borderline: the interval only just excludes zero' END AS note
FROM result_heating_demand h JOIN dim_city c ON c.city = h.city
UNION ALL
SELECT 'C8', 'Growing season, El Nino minus neutral', g.city, COALESCE(c.city_name, 'Ontario (average)'),
       g.diff_days, g.ci_lower, g.ci_upper, 'days', g.status = 'interval_excludes_zero', g.n_el_nino, g.n_neutral, NULL
FROM result_growing_season g LEFT JOIN dim_city c ON c.city = g.city
UNION ALL
SELECT CASE t.test WHEN 'freeze_thaw_days_vs_maple_residual' THEN 'C6'
                   WHEN 'freeze_thaw_days_el_nino_minus_neutral' THEN 'C7' ELSE 'C9' END,
       CASE t.test WHEN 'freeze_thaw_days_vs_maple_residual' THEN 'Freeze-thaw days vs maple production (r)'
                   WHEN 'freeze_thaw_days_el_nino_minus_neutral' THEN 'Freeze-thaw days, El Nino minus neutral'
                   ELSE 'GDP growth, El Nino minus neutral' END,
       'province', 'Ontario', t.estimate, t.ci_lower, t.ci_upper,
       CASE t.statistic WHEN 'pearson_r' THEN 'r' WHEN 'mean_difference_days' THEN 'days' ELSE 'percentage points' END,
       t.status = 'interval_excludes_zero', t.n_comparison, t.n_reference,
       CASE t.test WHEN 'freeze_thaw_days_vs_maple_residual'
                   THEN 'Real link, but not shown to be an El Nino effect (see C7)' END
FROM result_impact_tests t;
