-- BQ2 and BQ5: Did El Nino winters bring less snow and fewer snow days?

-- Total snowfall and snow days by ENSO group (K3, K4)
SELECT city_name, metric_label, enso_group, winters, ROUND(mean, 1) AS mean_value, unit
FROM v_dash_group_averages
WHERE metric IN ('snowfall_total_cm', 'snow_days')
ORDER BY metric_order, latitude_approx, group_order;

-- El Nino and strong El Nino minus neutral (C2, C3)
SELECT metric_label, city_name, comparison_group, ROUND(difference, 1) AS difference, unit,
       ROUND(ci_lower, 1) AS ci_lower, ROUND(ci_upper, 1) AS ci_upper,
       n_comparison, n_reference, result_label
FROM v_dash_comparison
WHERE metric IN ('snowfall_total_cm', 'snow_days') AND comparison_group IN ('El Nino', 'Strong El Nino')
ORDER BY metric_order, comparison_group, south_to_north;

-- Snow days in every strong El Nino winter at Toronto, against the neutral average
SELECT w.winter_label, w.snow_days,
       (SELECT ROUND(mean, 1) FROM v_dash_group_averages
        WHERE city = 'toronto' AND enso_group = 'Neutral' AND metric = 'snow_days') AS neutral_average
FROM v_winter_kpis w
WHERE w.city = 'toronto' AND w.strong_el_nino_roni = 1
ORDER BY w.winter_year;

-- Last winter with usable snowfall data at each station (why London and Thunder Bay results are weak)
SELECT c.city_name, MAX(CASE WHEN w.snowfall_pass = 1 THEN w.winter_year END) AS last_snowfall_winter,
       SUM(w.snowfall_pass) AS usable_snowfall_winters
FROM fact_winter_kpis w JOIN dim_city c ON c.city = w.city
GROUP BY c.city
ORDER BY c.latitude_approx;
