-- BQ7-BQ10: Do the winter differences reach heating, maple syrup, the growing season or the economy?

-- All impact results in one table (C5-C9), with caveats
SELECT comparison_id, impact, city_name, ROUND(estimate, 2) AS estimate, unit,
       ROUND(ci_lower, 2) AS ci_lower, ROUND(ci_upper, 2) AS ci_upper, is_significant, note
FROM v_dash_impacts
ORDER BY comparison_id, city_name;

-- BQ7: heating-degree-days, El Nino vs neutral winters, by station (K6, C5)
SELECT c.city_name, ROUND(h.neutral_mean_hdd) AS neutral_hdd, ROUND(h.el_nino_mean_hdd) AS el_nino_hdd,
       ROUND(h.pct, 1) AS pct_change, ROUND(h.pct_lo, 1) AS pct_lo, ROUND(h.pct_hi, 1) AS pct_hi, h.status
FROM result_heating_demand h JOIN dim_city c ON c.city = h.city
ORDER BY c.latitude_approx;

-- BQ8: the five best and five worst maple years against trend, with freeze-thaw days (K7, K8)
SELECT * FROM (SELECT year, ROUND(freeze_thaw_days, 1) AS freeze_thaw_days, ROUND(maple_residual) AS vs_trend_k_gal,
                      enso_class_roni, 'best' AS rank_group
               FROM result_maple_freeze_thaw ORDER BY maple_residual DESC LIMIT 5)
UNION ALL
SELECT * FROM (SELECT year, ROUND(freeze_thaw_days, 1), ROUND(maple_residual), enso_class_roni, 'worst'
               FROM result_maple_freeze_thaw ORDER BY maple_residual ASC LIMIT 5);

-- BQ9: average frost-free season by ENSO class of the preceding winter (K9)
SELECT c.city_name, e.enso_class_roni, COUNT(g.growing_season_days) AS years,
       ROUND(AVG(g.growing_season_days), 1) AS mean_days
FROM fact_growing_season g
JOIN dim_city c ON c.city = g.city
JOIN dim_enso_winter e ON e.winter_year = g.year
WHERE g.complete = 1
GROUP BY c.city, e.enso_class_roni
ORDER BY c.latitude_approx, e.enso_class_roni;

-- BQ10: Ontario GDP growth by ENSO class (K10)
SELECT e.enso_class_roni, COUNT(*) AS years, ROUND(AVG(g.gdp_growth_pct), 2) AS mean_growth_pct,
       ROUND(MIN(g.gdp_growth_pct), 2) AS worst_year_pct
FROM fact_ontario_gdp g JOIN dim_enso_winter e ON e.winter_year = g.year
WHERE g.gdp_growth_pct IS NOT NULL
GROUP BY e.enso_class_roni;
