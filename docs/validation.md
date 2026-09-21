# Verification of the included run

Verified September 21, 2026. These checks establish consistency with the supplied data and declared formulas; they do not certify source station measurements as error-free.

| Check | Result |
|---|---|
| Six input CSVs against the repository snapshot | Git blob hashes matched |
| Daily source-to-output reconciliation | All 98,096 source dates and original numeric measurements matched the enriched output |
| Source retention and daily joins | 98,096 rows retained; no duplicate `(city, date)` keys or join multiplication |
| Derived means | Exactly 3: Ottawa 2, Toronto 1; observed means remain separate |
| Winter table | 270 unique `(city, winter_year)` rows for six cities and 45 winters |
| Winter calculations | Recomputed all eligible means, snowfall sums, snow-day counts and cold-day counts from daily data |
| Ineligible metrics | Withheld independently as blank values |
| Baselines | Recomputed equal-weight eligible winter averages and counts for 1991–2020 at all six cities |
| Anomalies | Recomputed `mean_temp - baseline_mean_temp`; 85 eligible city-winter anomalies occur outside the baseline years |
| ENSO comparisons | Recomputed group sizes and differences for all 240 rows |
| Regional comparisons | Recomputed matching, sample sizes and paired difference-of-differences for all 20 rows |
| Focused automated tests | Seven tests passed |
| Charts | Twelve PNGs generated; representative distribution, comparison and timeline charts inspected for readability |

The seven automated tests cover: ENSO threshold boundaries; known NOAA snapshot values; conflicting/identical duplicates and missing values; leap calendars and complete counts; monthly missing-data boundaries; baseline application outside the baseline period; and bootstrap sign, repeatability and insufficient-group handling.

`results/run_manifest.json` captures the included calculation's source hashes, settings and runtime versions. PNG styling was refined after that calculation to share scales across comparison panels and move the timeline legend outside the data; the underlying numerical results were unchanged.

For your own rerun:

```powershell
python -m unittest discover -s tests -v
python python/run_pipeline.py
```

Every run also performs built-in key, row, calendar, ENSO-join, baseline, anomaly and eligibility checks before exporting. After replacing source files or changing rules, review the new audit reports and sample sizes before interpreting the updated charts.
