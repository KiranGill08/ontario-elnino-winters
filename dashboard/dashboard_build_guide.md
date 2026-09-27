# Dashboard Build Guide: Ontario Winters and El Niño

This guide is for whoever builds the Power BI dashboard. It explains what the dashboard must show, where every number comes from, how to connect to the data, and what to check before it is finished. Everything the dashboard needs is already calculated and stored in the project database; the dashboard only displays it. **No statistics need to be calculated in Power BI.**

## 1. What the project found, in brief

The dashboard presents a historical comparison of Ontario winters (December–February, 1981–82 to 2025–26, 45 winters) at six stations: Windsor, London, Toronto Pearson, Ottawa, Sudbury and Thunder Bay. Each winter is classed as El Niño, neutral or La Niña using NOAA's RONI index; five El Niño winters were strong.

The main messages the dashboard should make easy to see:

- **Strong El Niño winters were clearly warmer:** 2.4–4.1 °C warmer than neutral winters at five of six stations. For all El Niño winters together, every station was warmer, but no single station's result is certain.
- **The warming grows toward the north.** Thunder Bay had the largest difference (+4.1 °C in strong El Niño winters).
- **Southern stations had fewer snow days:** Toronto about 6 fewer per winter in El Niño winters, Windsor about 8 fewer.
- **Every El Niño comparison points the same way** (warmer, less snow, fewer snow days, fewer very cold days); 18 of 48 have intervals that exclude zero, one of them only just.
- **Beyond weather:** heating demand was lower in El Niño winters (clear only at Thunder Bay, and only just). Maple syrup is linked to spring freeze-thaw days, but that link is not shown to be an El Niño effect.

The full findings are in `reports/findings.md`. Business questions and KPI definitions are in `docs/kpis_and_business_questions.md`.

## 2. What to deliver

| Deliverable | Location |
|---|---|
| Power BI file | `dashboard/ontario_enso_dashboard.pbix` |
| One screenshot per page (PNG) | `dashboard/screenshots/` |
| PDF export of all pages (File → Export → Export to PDF) | `dashboard/ontario_enso_dashboard.pdf` |

The project plan requires three views: a **station map**, an **ENSO comparison** and a **historical timeline**. An **impacts** page and an **about** page are recommended. Keep each page simple: a clear title, one main visual, and one or two filters.

## 3. Get the data

The database is `sql/ontario_enso.db`, a single SQLite file already in the repository. You do not need to run any code to build the dashboard.

To rebuild it from scratch (only needed if the data or code changes):

```bash
pip install -r requirements.txt
python python/run_pipeline.py
python python/05_database/load_database.py
python python/05_database/check_winter_summary.py
```

To look inside the database before building, open it in [DB Browser for SQLite](https://sqlitebrowser.org/) (free). Ready-made queries for every business question are in `sql/queries/`.

## 4. Connect Power BI to SQLite

Power BI has no built-in SQLite connector; it connects through ODBC. One-time setup:

1. Install a **64-bit** SQLite ODBC driver for Windows (Power BI Desktop is 64-bit). A widely used free option is the SQLite ODBC Driver by Christian Werner (`sqliteodbc_w64.exe`).
2. Confirm the driver name: open **ODBC Data Sources (64-bit)** from the Windows Start menu → *Drivers* tab. It is usually `SQLite3 ODBC Driver`.
3. In Power BI Desktop: **Home → Get Data → ODBC**. Leave *Data source name* as *(None)*, open *Advanced options*, and enter (with your own path):
   ```
   Driver={SQLite3 ODBC Driver};Database=C:\path\to\ontario-elnino-winters\sql\ontario_enso.db;
   ```
4. If asked for credentials, choose *Default or Custom* and connect without a user name.
5. In the Navigator, tick the tables listed in section 5 and choose **Transform Data** (not Load) so you can set data types first.

## 5. Tables to import

Import only these. Each `v_dash_` view is already shaped for one page, with readable labels and sort columns.

| Import | Rows | Used on |
|---|---:|---|
| `v_dash_map` | 6 | Map page |
| `v_dash_comparison` | 72 | Comparison page |
| `v_dash_group_averages` | 120 | Comparison page (averages) and cards |
| `v_dash_timeline` | 270 | Timeline page |
| `v_dash_impacts` | 16 | Impacts page |
| `result_maple_freeze_thaw` | 44 | Impacts page (maple scatter) |
| `dim_metric` | 5 | Optional: a shared metric slicer |

The views do not need relationships to each other; each page uses one view. Do not import the `fact_` tables unless you want extra detail pages.

### Columns

**`v_dash_map`**: one row per station.
`city`, `city_name`, `region`, `latitude_approx`, `map_location` (for example "Thunder Bay, Ontario, Canada"), `south_to_north` (1 = Windsor … 6 = Thunder Bay), `temperature_winters`, `snowfall_winters` (usable winters), `el_nino_temp_diff_c`, `strong_temp_diff_c`, `strong_temp_significant`, `el_nino_snow_days_diff`, `el_nino_snow_days_significant`.

**`v_dash_comparison`**: one row per station × measure × ENSO group (El Niño, strong El Niño, La Niña), each compared with neutral winters.
`city`, `city_name`, `latitude_approx`, `south_to_north`, `metric`, `kpi_id` (K2–K5), `metric_label`, `unit`, `metric_order`, `comparison_group`, `group_order`, `comparison_mean`, `reference_mean`, `difference`, `ci_lower`, `ci_upper`, `n_comparison`, `n_reference`, `is_significant`, `is_borderline`, `result_label` (*Clear difference*, *Borderline* or *Inconclusive*), `comparison_years`, `reference_years`.

**`v_dash_group_averages`**: one row per station × measure × ENSO group (La Niña, neutral, El Niño, strong El Niño).
`city`, `city_name`, `latitude_approx`, `metric`, `metric_label`, `unit`, `metric_order`, `enso_group`, `group_order`, `winters`, `mean`, `median`, `min`, `max`.

**`v_dash_timeline`**: one row per station × winter.
`city`, `city_name`, `latitude_approx`, `winter_year`, `winter_label` (for example "1997-98"), `temp_anomaly` (°C, blank when the winter failed the data-quality rule), `roni_djf`, `enso_class_roni`, `strong_el_nino_roni`, `trend_fit` (the station's warming-trend line, °C), `slope_c_per_decade`, `excluded`.

**`v_dash_impacts`**: one row per impact result.
`comparison_id` (C5–C9), `impact`, `city`, `city_name`, `estimate`, `ci_lower`, `ci_upper`, `unit`, `is_significant`, `n_comparison`, `n_reference`, `note` (caveats).

**`result_maple_freeze_thaw`**: one row per year, 1982–2025.
`year`, `syrup_thousand_gallons`, `maple_trend`, `maple_residual` (production above or below trend), `freeze_thaw_days` (Feb–Apr, average of six stations), `fitted_residual`, `enso_class_roni`, `enso_class_oni`.

## 6. Prepare the data in Power Query and the model

Do these once, before building visuals.

1. **Data types.** True/false columns arrive as 1/0 (`is_significant`, `is_borderline`, `strong_temp_significant`, `el_nino_snow_days_significant`, `strong_el_nino_roni`, `excluded`). Set them to *True/False*. Set `winter_year` and `year` to *Whole number*. All differences, intervals and means are *Decimal number*.
2. **Stop Power BI from adding up results.** In the model view, select every numeric result column (`difference`, `ci_lower`, `ci_upper`, `mean`, `median`, `estimate`, `temp_anomaly`, `trend_fit` and the `_diff` columns) and set **Summarization = Don't summarize**. Adding or averaging differences across stations produces meaningless numbers.
3. **Sort order.** Select a column, then *Column tools → Sort by column*:
   - `city_name` → `south_to_north` (stations run south to north, as in the report)
   - `comparison_group` → `group_order`; `enso_group` → `group_order`
   - `metric_label` → `metric_order`
   - `winter_label` → `winter_year`
4. **Missing values.** Blank `temp_anomaly` values are winters with too much missing data. Leave them blank; never replace them with 0.

## 7. Page-by-page design

Use one colour per ENSO group everywhere, matching the report's charts:

| Group | Colour |
|---|---|
| La Niña | `#2866A6` (blue) |
| Neutral | `#64748B` (grey) |
| El Niño | `#B5482D` (red-orange) |
| Strong El Niño | `#7A2512` (dark red) |

Put units in every axis title (°C, cm, days). Never put °C, cm and days on the same axis.

### Page 1: Overview and station map

**Question answered:** where are the stations, and what is the headline at each?

- **Map visual.** Source `v_dash_map`. *Location* = `map_location`; *Bubble size* = `strong_temp_diff_c`; tooltips: `city_name`, `strong_temp_diff_c`, `strong_temp_significant`, `el_nino_snow_days_diff`, `temperature_winters`, `snowfall_winters`. If the Map visual is disabled, enable it under *File → Options and settings → Options → Global → Security → Map and Filled Map visuals*, or use the Azure Maps visual.
- **Three cards** across the top: "Strong El Niño winters: +2.4 to +4.1 °C warmer at 5 of 6 stations", "Toronto: 6 fewer snow days in El Niño winters", "18 of 48 El Niño comparisons clear zero (1 only just)". Cards can be text boxes; the numbers are fixed results.
- **Table** with `city_name`, `strong_temp_diff_c`, `el_nino_snow_days_diff`, `temperature_winters`, `snowfall_winters`, sorted south to north.
- **Footer text:** "Historical comparison, winters 1981–82 to 2025–26. Not a forecast. ENSO classes from NOAA RONI."

### Page 2: ENSO comparison

**Question answered:** how much did El Niño winters differ from neutral winters, and how certain is it? (BQ1–BQ6)

- **Slicers:** `metric_label` (single select, default *Temperature anomaly*) and `comparison_group` (default *El Niño* and *Strong El Niño*).
- **Main visual:** clustered bar chart. Axis = `city_name`; Values = `difference`; Legend = `comparison_group`. Add the 95% interval with **Analytics pane → Error bars**: upper bound `ci_upper`, lower bound `ci_lower`. If error bars are not available in your version, use a table with the interval columns instead.
- **Zero reference line** (Analytics pane → Constant line at 0). Bars whose error bar crosses the zero line are inconclusive.
- **Conditional formatting:** colour or label bars by `result_label`. *Borderline* results must look different from *Clear difference*, for example hatched or lighter.
- **Tooltip:** `comparison_mean`, `reference_mean`, `n_comparison`, `n_reference`, `comparison_years`, `result_label`.
- **Supporting visual:** clustered column chart of `v_dash_group_averages[mean]` by `city_name` and `enso_group`, filtered by the same `metric_label`. This shows the actual averages behind the differences. Tooltip: `winters`, `median`, `min`, `max`.
- **Text box:** "Bars show El Niño (or strong El Niño) minus neutral winters. Lines show the 95% interval; if a line crosses zero the difference is inconclusive. Neutral groups contain only 7–9 winters, so intervals are wide."

### Page 3: Historical timeline

**Question answered:** how have winters changed over 45 years, and where do El Niño winters sit? (BQ1, trend check)

- **Slicer:** `city_name` (single select, default Toronto Pearson).
- **Main visual:** line chart. X-axis = `winter_year`; Y-axis = `trend_fit` as a dashed line. Add `temp_anomaly` as markers coloured by `enso_class_roni` (for example, a combo of a line chart and a scatter chart on the same axes, or a scatter chart with `trend_fit` added as a line).
- **Zero line** at 0 °C: the station's 1991–2020 average.
- **Card:** `slope_c_per_decade` for the selected station, labelled "Warming trend (°C per decade)".
- **Text box:** "Blank years are winters with too much missing data. Removing the warming trend does not change the El Niño results."

### Page 4: Impacts beyond the weather (optional)

**Question answered:** do the winter differences reach heating, maple syrup, the growing season or the economy? (BQ7–BQ10)

- **Table** from `v_dash_impacts`: `impact`, `city_name`, `estimate`, `unit`, `ci_lower`, `ci_upper`, `is_significant`, `note`. The `note` column must be visible: it holds the caveats.
- **Bar chart:** heating demand by station, filtered to `comparison_id = C5`, with error bars from `ci_lower` and `ci_upper`.
- **Scatter chart** from `result_maple_freeze_thaw`: X = `freeze_thaw_days`, Y = `maple_residual`, Details = `year`, with a trend line (Analytics pane). Caption: "More freeze-thaw days in Feb–Apr, more maple syrup (r = +0.28). El Niño does not significantly change freeze-thaw days, so this is not shown to be an El Niño effect."

### Page 5: About and data quality (recommended)

- Data sources: Environment and Climate Change Canada daily station data; NOAA RONI and ONI; Statistics Canada tables 32-10-0354-01 (maple) and 36-10-0222-01 (GDP).
- Usable winters per station from `v_dash_map` (`temperature_winters`, `snowfall_winters`).
- The limitations listed in section 8.

## 8. Wording and accuracy rules

These keep the dashboard consistent with the report. Please follow them exactly.

1. **Historical, not a forecast.** Never phrase a result as what will happen next winter.
2. **Association, not cause.** Say "El Niño winters were warmer", not "El Niño caused warmer winters".
3. **Show uncertainty with every difference:** the interval, or at least the *Clear difference / Borderline / Inconclusive* label.
4. **Inconclusive does not mean no effect.** It means the data cannot tell.
5. **Two borderline results** must never be shown as firm findings: Thunder Bay heating demand (interval ends at −0.00%) and London's strong El Niño snowfall (interval ends at −0.4 cm).
6. **Snow data is limited at London and Thunder Bay** (snowfall records end around 2003; 20 and 12 usable winters of 45). Add a note wherever their snow results appear.
7. **The maple result always travels with its caveat:** not shown to be an El Niño effect.
8. **Heating-degree-days are a demand measure,** not energy use or cost. Do not show dollar figures.
9. **Missing data is blank, never zero.**

## 9. Check your numbers

Before finishing, confirm the dashboard shows these values. They come from the database and match the report.

| Where | What | Expected |
|---|---|---|
| Comparison page, temperature anomaly, strong El Niño | Windsor / London / Toronto / Ottawa / Sudbury / Thunder Bay | +2.57 / +2.58 / +2.37 / +1.41 / +3.07 / +4.08 °C |
| Comparison page, snow days, El Niño | Toronto Pearson | −6.13 days, interval −9.57 to −2.47 |
| Comparison page, all measures, El Niño and strong El Niño | Result labels | 17 Clear difference, 1 Borderline, 30 Inconclusive |
| Group averages, Toronto snow days | La Niña / Neutral / El Niño / Strong El Niño | 19.0 / 20.75 / 14.62 / 11.4 days |
| Timeline, warming trend (°C per decade) | Windsor / London / Toronto / Ottawa / Sudbury / Thunder Bay | 0.18 / 0.27 / 0.48 / 0.27 / 0.15 / 0.33 |
| Timeline | Winters shown | 1982–2026; 17 station-winters blank |
| Impacts | Maple vs freeze-thaw | r = +0.28, interval +0.06 to +0.49 |

If a number differs, the usual causes are summarization left on (section 6, step 2), a slicer still filtering, or a data type left as text.

## 10. Updating the dashboard later

If the pipeline or data changes, rebuild the database (section 3), then click **Refresh** in Power BI. The views keep the same names and columns, so the visuals update automatically. Close Power BI and DB Browser before rebuilding: the database file cannot be replaced while another program has it open.

## 11. Troubleshooting

| Problem | Fix |
|---|---|
| "Data source name not found" or driver error | The driver name in the connection string must match *ODBC Data Sources (64-bit) → Drivers* exactly, and the driver must be 64-bit. |
| Numbers are far too large | Summarization is set to Sum. Set *Don't summarize* (section 6, step 2). |
| Stations in alphabetical order | Set *Sort by column* on `city_name` (section 6, step 3). |
| True/false columns show 0 and 1 | Change their type to *True/False* in Power Query. |
| Map shows no bubbles | Enable Map visuals in Options → Security, and check that `map_location` is in the *Location* field. |
| Load or refresh fails with "database is locked" | Close DB Browser or any other program that has `ontario_enso.db` open. |
| A view is missing | Rebuild the database (section 3); the loader creates all views. |

## 12. Where to find more

| Need | File |
|---|---|
| Findings and interpretation | `reports/findings.md` |
| Business questions, KPI and comparison definitions (K1–K10, C1–C9, S1–S6) | `docs/kpis_and_business_questions.md` |
| Every column in every table | `docs/data_dictionary.md` |
| Database tables, views and queries | `sql/README.md`, `sql/dashboard_views.sql`, `sql/queries/` |
| Report charts, for visual reference | `reports/figures/` |
