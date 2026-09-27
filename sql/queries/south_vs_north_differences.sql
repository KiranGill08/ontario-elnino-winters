-- BQ4: Was the El Nino pattern different between southern and northern stations?

-- El Nino minus neutral temperature, south to north
SELECT city_name, ROUND(latitude_approx, 1) AS latitude, comparison_group,
       ROUND(difference, 2) AS difference_c, result_label
FROM v_dash_comparison
WHERE metric = 'temp_anomaly' AND comparison_group IN ('El Nino', 'Strong El Nino')
ORDER BY comparison_group, south_to_north;

-- Is Thunder Bay's El Nino effect larger than the south's? Difference of differences (S4)
SELECT r.north_city, r.south_city, r.metric,
       ROUND(r.difference_of_differences, 2) AS north_minus_south, ROUND(r.ci_lower, 2) AS ci_lower,
       ROUND(r.ci_upper, 2) AS ci_upper, r.status, r.n_common_el_nino, r.n_common_neutral
FROM result_regional_comparisons r
WHERE r.enso_index = 'RONI' AND r.metric IN ('temp_anomaly', 'snow_days', 'days_below_m20')
ORDER BY r.metric, r.south_city;

-- Headline results per station (the map page)
SELECT south_to_north, city_name, ROUND(el_nino_temp_diff_c, 2) AS el_nino_temp_c,
       ROUND(strong_temp_diff_c, 2) AS strong_temp_c, strong_temp_significant,
       ROUND(el_nino_snow_days_diff, 1) AS el_nino_snow_days, el_nino_snow_days_significant
FROM v_dash_map
ORDER BY south_to_north;
