-- Winter summary in SQL: the same table pandas writes to data/enso_group_summary.csv.
-- One row per city, ENSO index (RONI/ONI), ENSO group and KPI, with the number of winters,
-- how many passed the data-quality rule, and mean, median, standard deviation, min and max.
-- "Strong El Nino" is a subset of "El Nino" (index of +1.5 or more), as in pandas.
--
-- Built from fact_winter_kpis and dim_enso_winter by python/05_database/load_database.py and
-- saved as the table result_winter_summary_sql, so any tool (Power BI, DB Browser) can read it.
-- Check it against pandas with python/05_database/check_winter_summary.py.

DROP TABLE IF EXISTS result_winter_summary_sql;

CREATE TABLE result_winter_summary_sql AS
WITH kpi AS (   -- one row per city, winter and KPI; value is NULL when the winter failed the quality rule
    SELECT city, winter_year, 'mean_temp' AS metric, 'C' AS unit, mean_temp AS value FROM fact_winter_kpis
    UNION ALL SELECT city, winter_year, 'temp_anomaly', 'C', temp_anomaly FROM fact_winter_kpis
    UNION ALL SELECT city, winter_year, 'snowfall_total_cm', 'cm', snowfall_total_cm FROM fact_winter_kpis
    UNION ALL SELECT city, winter_year, 'snow_days', 'days', snow_days FROM fact_winter_kpis
    UNION ALL SELECT city, winter_year, 'days_below_m20', 'days', days_below_m20 FROM fact_winter_kpis
),
grp AS (        -- which ENSO group(s) each winter belongs to, under each index
    SELECT winter_year, 'RONI' AS enso_index, enso_class_roni AS enso_group FROM dim_enso_winter
    UNION ALL SELECT winter_year, 'RONI', 'Strong El Nino' FROM dim_enso_winter WHERE strong_el_nino_roni = 1
    UNION ALL SELECT winter_year, 'ONI', enso_class_oni FROM dim_enso_winter
    UNION ALL SELECT winter_year, 'ONI', 'Strong El Nino' FROM dim_enso_winter WHERE strong_el_nino_oni = 1
),
joined AS (     -- each value with its position in the group (for the median) and the group mean (for the std)
    SELECT k.city, g.enso_index, g.enso_group, k.metric, k.unit, k.winter_year, k.value,
           ROW_NUMBER() OVER w_sorted AS rn,
           COUNT(k.value) OVER w_all AS n_valid,
           AVG(k.value) OVER w_all AS group_mean
    FROM kpi k
    JOIN grp g ON g.winter_year = k.winter_year
    WINDOW w_all AS (PARTITION BY k.city, g.enso_index, g.enso_group, k.metric),
           w_sorted AS (PARTITION BY k.city, g.enso_index, g.enso_group, k.metric
                        ORDER BY k.value IS NULL, k.value)
)
SELECT j.city, j.enso_index, j.enso_group, j.metric, j.unit,
       COUNT(*)                                                         AS n_group_winters,
       COUNT(j.value)                                                   AS n_eligible,
       AVG(j.value)                                                     AS mean,
       AVG(CASE WHEN j.rn IN ((j.n_valid + 1) / 2, (j.n_valid + 2) / 2) THEN j.value END) AS median,
       CASE WHEN COUNT(j.value) > 1
            THEN sqrt(SUM((j.value - j.group_mean) * (j.value - j.group_mean)) / (COUNT(j.value) - 1))
       END                                                              AS std,
       MIN(j.value)                                                     AS min,
       MAX(j.value)                                                     AS max,
       (SELECT group_concat(y, ',') FROM (
            SELECT k2.winter_year AS y FROM joined k2
            WHERE k2.city = j.city AND k2.enso_index = j.enso_index AND k2.enso_group = j.enso_group
              AND k2.metric = j.metric AND k2.value IS NOT NULL
            ORDER BY k2.winter_year))                                   AS eligible_years
FROM joined j
GROUP BY j.city, j.enso_index, j.enso_group, j.metric, j.unit;
