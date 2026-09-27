-- BQ3: Did El Nino winters have fewer very cold days (-20 C or colder)?

-- Average very cold days by ENSO group (K5)
SELECT city_name, enso_group, winters, ROUND(mean, 1) AS mean_days, min, max
FROM v_dash_group_averages
WHERE metric = 'days_below_m20'
ORDER BY latitude_approx, group_order;

-- El Nino and strong El Nino minus neutral (C4)
SELECT city_name, comparison_group, ROUND(difference, 1) AS difference_days,
       ROUND(ci_lower, 1) AS ci_lower, ROUND(ci_upper, 1) AS ci_upper, result_label
FROM v_dash_comparison
WHERE metric = 'days_below_m20' AND comparison_group IN ('El Nino', 'Strong El Nino')
ORDER BY comparison_group, south_to_north;

-- Severe cold still happens in El Nino winters: the coldest El Nino winter at each station
SELECT city_name, winter_label, days_below_m20
FROM (SELECT city_name, winter_label, days_below_m20, latitude_approx,
             ROW_NUMBER() OVER (PARTITION BY city ORDER BY days_below_m20 DESC) AS rn
      FROM v_winter_kpis
      WHERE enso_class_roni = 'El Nino' AND days_below_m20 IS NOT NULL)
WHERE rn = 1
ORDER BY latitude_approx;

-- The coldest days of the 1997-98 strong El Nino winter at Thunder Bay (daily detail)
SELECT date, tmin, tmax, snowfall_cm
FROM v_daily_weather
WHERE city = 'thunderbay' AND winter_year = 1998 AND is_winter = 1
ORDER BY tmin
LIMIT 5;
