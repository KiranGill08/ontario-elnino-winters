-- Data quality: how much usable data supports each result?

-- Usable winters per station and measure (the usability grid in numbers)
SELECT city_name, temperature_winters, snowfall_winters,
       (SELECT SUM(cold_days_pass) FROM fact_winter_kpis w WHERE w.city = m.city) AS cold_day_winters
FROM v_dash_map m
ORDER BY south_to_north;

-- Winters excluded from the temperature KPIs, and why (missing-data rule)
SELECT c.city_name, w.winter_label, w.valid_temperature_days, w.expected_days, w.missing_calendar_days
FROM fact_winter_kpis w JOIN dim_city c ON c.city = w.city
WHERE w.temperature_pass = 0
ORDER BY c.latitude_approx, w.winter_year;

-- Each station's 1991-2020 baseline for the temperature anomaly (K2)
SELECT c.city_name, ROUND(b.baseline_mean_temp, 2) AS baseline_c, b.baseline_n_winters, b.baseline_status
FROM result_city_baselines b JOIN dim_city c ON c.city = b.city
ORDER BY c.latitude_approx;

-- ENSO classes and strong El Nino winters under RONI and ONI
SELECT enso_class_roni, COUNT(*) AS winters, SUM(strong_el_nino_roni) AS strong,
       GROUP_CONCAT(CASE WHEN strong_el_nino_roni = 1 THEN winter_year END) AS strong_winters
FROM dim_enso_winter
GROUP BY enso_class_roni;

-- Which pipeline run is loaded
SELECT run_folder, pipeline_completed_utc, loaded_utc, validation FROM meta_pipeline_runs;
