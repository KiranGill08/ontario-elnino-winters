# Data dictionary

## Choose the right table

Use `results/data/winter_kpis.csv` for winter analysis: its unique key is `(city, winter_year)`. It has 270 rows: six cities × 45 winters, including winters whose measurements fail eligibility checks.

Use a daily enriched CSV to inspect measurements. Its unique key is `(city, date)`. The combined file contains the same observations as the six individual files; do not import both into the same table. Missing calendar dates are reported separately, not inserted as invented observations.

**Winter KPIs repeat on each daily row belonging to that winter. Do not sum or average those repeated fields across daily rows to summarize winters.** Use the winter table, which gives each winter one row.

Blank numeric fields mean missing, unavailable or ineligible, depending on the accompanying quality fields. They never mean zero. CSV booleans are `True`/`False`; an absent winter-level field on a daily row is blank. For MySQL, convert booleans to 1/0 and blanks to SQL NULL before loading. Treat `station_id` as an identifier, not a measurement.

## Location and source fields

| Field | Meaning |
|---|---|
| `city` | Stable lower-case key: london, ottawa, sudbury, thunderbay, toronto, windsor |
| `city_name` | Display name; the Toronto series is labelled Toronto Pearson |
| `region` | Descriptive Ontario region configured for this project |
| `latitude_approx` | Approximate latitude for display ordering; not a verified coordinate for every historical station |
| `included_in_proposal` | True for Windsor, Toronto, Ottawa and Thunder Bay |
| `included_in_repo_study` | True for the four proposal cities plus Sudbury |
| `station_id` | Source station identifier; retained to review station changes |
| `source_file`, `source_row` | Original filename and CSV line number, with the header counted as line 1 |
| `quality_notes` | Cleaning/derivation notes; blank when no note applies |

## Daily measurements and features

| Field | Meaning / unit |
|---|---|
| `date` | Observation date, YYYY-MM-DD |
| `year`, `month` | Calendar year and month |
| `tmax`, `tmin`, `tmean` | Source daily maximum, minimum and observed mean temperature, °C; invalid screened measurements are withheld, with source retained under `data/raw/` |
| `tmean_analysis` | Observed valid mean, otherwise `(tmax + tmin) / 2` only when the mean was originally missing and both same-day extremes are valid |
| `tmean_derived` | True when that same-day calculation supplied the analysis mean |
| `rain_mm` | Source daily rainfall, mm |
| `snowfall_cm` | Source daily new snowfall, cm; not snow depth |
| `precip_mm` | Source total precipitation, mm; do not add rainfall mm and snowfall cm to reconstruct this field |
| `snow_day` | 1 when valid snowfall ≥1 cm, 0 when valid snowfall <1 cm, blank when snowfall is missing |
| `very_cold_day` | 1 when valid minimum temperature ≤−20°C, 0 otherwise, blank when minimum temperature is missing |
| `is_winter` | True for December, January and February |
| `winter_year` | Ending year of a DJF winter; December 1981 belongs to 1982. Blank for other months |
| `in_study_period` | True for a DJF observation belonging to a winter ending 1982–2026 |

Daily event flags exist for all months. Filter `in_study_period` when answering winter questions. January–February 1981 are preserved but are outside the first complete study winter. Non-study rows do not receive study winter KPIs.

## Winter KPIs and baseline fields

| Field | Meaning / unit |
|---|---|
| `winter_label` | Human-readable season such as 1981-82 |
| `winter_start`, `winter_end` | December 1 of the previous year and February 28/29 of the ending year |
| `mean_temp` | K1: mean of available valid daily analysis means after all three monthly temperature checks pass, °C |
| `temp_anomaly` | K2: `mean_temp - baseline_mean_temp`, °C difference |
| `snowfall_total_cm` | K3: sum of daily snowfall only when every expected winter day has valid snowfall, cm |
| `snow_days` | K4: number of winter days with snowfall ≥1 cm, using the same complete-snowfall requirement |
| `days_below_m20` | K5: number of winter days with minimum temperature ≤−20°C; requires valid minima on every expected day. The threshold is inclusive despite the short column name |
| `baseline_mean_temp` | Equal-weight mean of eligible K1 values for winters ending 1991–2020 at this city |
| `baseline_n_winters` | Actual number of eligible winters used, at most 30 |
| `baseline_start_winter`, `baseline_end_winter` | Requested baseline ending years, 1991 and 2020 |
| `baseline_complete` | True if all 30 baseline winters qualify |
| `baseline_status` | `complete`, `partial_available_winter_average` or `unavailable`; partial values use the eligible subset, without filling gaps |
| `temp_detrended_residual` | Observed K1 minus a fitted city-specific linear trend; used only for a sensitivity comparison, °C |

The six-row `city_baselines.csv` holds the baseline values once per city. The anomaly applies to all eligible study winters, not just the baseline period. December 1990 is included because the winter ending 1991 starts then.

## Winter quality fields

| Field | Meaning |
|---|---|
| `expected_days` | 90 or 91, from the full DJF calendar |
| `recorded_days` | Number of cleaned source dates present in the winter |
| `missing_calendar_days` | Expected dates absent from the source |
| `valid_temperature_days`, `valid_snowfall_days` | Expected dates with valid analysis means / snowfall measurements |
| `derived_temperature_days` | Number of winter means calculated from same-day extremes |
| `temperature_pass` | Every month has ≤5 missing analysis means and no missing run longer than 3 days |
| `snowfall_pass` | All expected winter days have valid snowfall |
| `cold_days_pass` | All expected winter days have valid minimum temperatures |
| `temperature_coverage_pct`, `snowfall_coverage_pct` | Respective valid-day count ÷ expected days ×100 |
| `derived_temperature_share_pct` | Derived means ÷ valid analysis means ×100 |
| `exclusion_reasons` | Reasons individual winter metrics were withheld |
| `quality_method` | Identifier of the implemented eligibility policy |

Missing runs are evaluated separately within each calendar month. See `reports/monthly_quality.csv` for month-level counts and longest runs, `missing_winter_dates.csv` for absent dates, and `winter_exclusions.csv` for failed winter checks. A temperature pass does not imply a snowfall or cold-count pass.

## ENSO fields

| Field | Meaning |
|---|---|
| `oni_djf`, `roni_djf` | NOAA DJF ONI and RONI, respectively, from the archived ERSSTv6 snapshot |
| `enso_class_oni`, `enso_class_roni` | `El Nino` for index ≥0.5, `La Nina` for index ≤−0.5, otherwise `Neutral` |
| `strong_el_nino_oni`, `strong_el_nino_roni` | True for index ≥1.5; strong events remain part of the El Niño class |
| `enso_index`, `enso_value`, `enso_class`, `strong_el_nino` | Primary index and corresponding fields; ONI by default |

`enso_winter_labels.csv` provides one row per winter. Group-summary and comparison tables hold both indices regardless of the primary chart setting.

## Group and comparison tables

`enso_group_summary.csv` contains one row per city, index, group and metric. It reports valid counts, mean, median, standard deviation, minimum, maximum and the included winter years. A strong-event group overlaps the El Niño group.

In `enso_comparisons.csv`, `difference = comparison_mean - reference_mean`. `metric` names the KPI; `comparison_group` and `reference_group` identify the two samples. `n_comparison` and `n_reference` count eligible winters for this specific metric; their year lists make exclusions visible.

`ci_lower` and `ci_upper` are percentile 95% intervals from 10,000 whole-winter resamples within each group. `status` records whether the interval includes zero, excludes zero or cannot be estimated. A sample with fewer than two winters in either group has no interval. `sample_note` highlights small groups; `bootstrap_samples` records the requested repetitions. Intervals are exploratory and are not corrected for multiple comparisons.

`regional_comparisons.csv` uses only common eligible years for each city pair. Its difference is **(Thunder Bay minus southern city in El Niño winters) minus (Thunder Bay minus southern city in neutral winters)**. It is not a province-wide average or causal effect.

`temperature_trends.csv` reports each city's fitted slope in °C per decade, intercept and eligible sample size. `temperature_trend_sensitivity.csv` repeats group comparisons on fitted residuals. Its intervals condition on the fitted trend and do not include uncertainty from estimating that trend.

## Reading with pandas

```python
import pandas as pd

daily = pd.read_csv("results/data/all_stations_daily_enriched.csv",
                    parse_dates=["date"], low_memory=False)
winters = pd.read_csv("results/data/winter_kpis.csv")
core = winters.loc[winters["included_in_proposal"]].copy()
```

Keep `city` plus `winter_year` as the winter key, and join daily to winter data with a many-to-one validation. Files in `reports/` are audit outputs; preserve them alongside the analysis tables.
