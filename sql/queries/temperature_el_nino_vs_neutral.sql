-- BQ1 and BQ6: Were El Nino winters warmer, and more so in strong El Nino winters?
-- Run on sql/ontario_enso.db (DB Browser for SQLite: Execute SQL). RONI is the primary index.

-- Average temperature anomaly by ENSO group and station (K2)
SELECT city_name, enso_group, winters, ROUND(mean, 2) AS mean_anomaly_c
FROM v_dash_group_averages
WHERE metric = 'temp_anomaly'
ORDER BY latitude_approx, group_order;

-- El Nino and strong El Nino minus neutral, with 95% intervals (C1, BQ6)
SELECT city_name, comparison_group, ROUND(difference, 2) AS difference_c,
       ROUND(ci_lower, 2) AS ci_lower, ROUND(ci_upper, 2) AS ci_upper,
       n_comparison, n_reference, result_label
FROM v_dash_comparison
WHERE metric = 'temp_anomaly' AND comparison_group IN ('El Nino', 'Strong El Nino')
ORDER BY comparison_group, south_to_north;

-- Does a stronger El Nino mean a warmer winter? Slope per unit of RONI (S3)
SELECT c.city_name, s.n_winters, ROUND(s.slope_c_per_index_unit, 2) AS slope_c_per_unit,
       ROUND(s.ci_lower, 2) AS ci_lower, ROUND(s.ci_upper, 2) AS ci_upper, ROUND(s.pearson_r, 2) AS r
FROM result_index_slopes s JOIN dim_city c ON c.city = s.city
WHERE s.enso_index = 'RONI'
ORDER BY c.latitude_approx;

-- Is the signal just long-term warming? The same comparison after removing each station's trend (S2)
SELECT c.city_name, t.comparison_group, ROUND(t.difference, 2) AS detrended_difference_c,
       ROUND(t.ci_lower, 2) AS ci_lower, ROUND(t.ci_upper, 2) AS ci_upper, t.status
FROM result_trend_sensitivity t JOIN dim_city c ON c.city = t.city
WHERE t.enso_index = 'RONI' AND t.reference_group = 'Neutral'
  AND t.comparison_group IN ('El Nino', 'Strong El Nino')
ORDER BY t.comparison_group, c.latitude_approx;

-- Warming trend per station, degrees per decade (S1)
SELECT c.city_name, t.n_winters, ROUND(t.slope_c_per_decade, 2) AS c_per_decade
FROM result_temperature_trends t JOIN dim_city c ON c.city = t.city
ORDER BY c.latitude_approx;

-- Warmest 10 station-winters, with their ENSO class
SELECT city_name, winter_label, ROUND(temp_anomaly, 2) AS anomaly_c, enso_class_roni, roni_djf
FROM v_winter_kpis
WHERE temp_anomaly IS NOT NULL
ORDER BY temp_anomaly DESC
LIMIT 10;
