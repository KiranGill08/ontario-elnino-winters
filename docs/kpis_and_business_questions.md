# Ontario El Niño Winters: Business Questions and KPIs

Prepared: September 21, 2026 · Updated: September 26, 2026 (impact KPIs, supporting metrics, settled decisions)  
Based on: `Ontario_ElNino_Proposal_and_4Week_Roadmap(2).md`, Part A, sections 3, 5, 10–12 and 15.  
Data checked: [GitHub interim data folder](https://github.com/KiranGill08/ontario-elnino-winters/tree/main/data/interim).

## 1. Project purpose

**Main question: Were El Niño winters in Ontario warmer, less snowy, or less extreme than other winters, and did the pattern differ from south to north?**

The project compares historical winters from **1981–82 through 2025–26: 45 winters**. It provides historical context for winter planning. It does not predict the next winter or establish that El Niño caused the observed differences.

A business question describes what a reader wants to know. A KPI is the measurement used to answer it. Here, “KPI” means a key climate indicator; the proposal does not define financial performance targets. Warmer or less snowy does not automatically mean better for every stakeholder.

Potential users include municipal winter-maintenance planners, winter-tourism operators, and community cold-weather planners. Weather patterns can inform planning discussions, but these CSVs cannot establish staffing requirements, salt budgets, operating savings, energy use, or tourism revenue.

## 2. Scope and available data

The attached proposal defines four main locations. The linked folder contains six candidate location files:

| File | Location | Role in the attached proposal | Source rows |
|---|---|---|---:|
| `windsor_daily.csv` | Windsor | Main location: southwest | 15,088 |
| `toronto_daily.csv` | Toronto Pearson | Main location: southern/central Ontario | 16,626 |
| `ottawa_daily.csv` | Ottawa | Main location: eastern Ontario | 16,628 |
| `thunderbay_daily.csv` | Thunder Bay | Main location: northwest | 16,480 |
| `sudbury_daily.csv` | Sudbury | Backup for Ottawa or optional extension | 16,602 |
| `london_daily.csv` | London | Optional extension | 16,672 |
| **Total** | **Six files** | **All six are included in the final analysis** | **98,096** |

**Decision (September 2026):** all six locations are analysed and reported. Snowfall results for London and Thunder Bay rest on few winters because those stations stopped reporting snowfall around 2003; the report states this with every snow result.

The file hashes checked on September 21 match the six files previously inspected in full. The rows include all seasons; only December, January and February within the study period enter the winter analysis. Row totals do not prove complete coverage.

All six files contain:

`date, tmax, tmin, tmean, rain_mm, snowfall_cm, precip_mm, station_id`

Add a `city` or stable analysis-location identifier from the filename. Keep `station_id` for tracing changes between source station records. Calculate location-level summaries across the documented station sequence rather than accidentally splitting one location into separate studies whenever an ID changes.

**Additional input needed:** an ENSO index table. The six daily weather CSVs do not contain ONI/RONI values or ENSO classes. Join one December–February index value to each winter using `winter_year`.

## 3. Business questions

The first four questions correspond to the proposal's research questions. Questions 5 and 6 expand measures and comparisons already included in its analysis plan.

| ID | Business question in simple English | KPI or comparison | Why the answer matters | Suggested visual |
|---|---|---|---|---|
| BQ1 | Were El Niño winters warmer than neutral winters at each location? | Mean winter temperature, temperature anomaly, and El Niño minus neutral temperature difference | Describes how seasonal temperature conditions differed historically | Temperature-anomaly box plot by ENSO class; difference chart with confidence intervals |
| BQ2 | Did El Niño winters receive less or more snowfall than neutral and La Niña winters? | Total winter snowfall; primary difference: El Niño minus neutral snowfall | Provides context about historical snowfall amounts for maintenance and winter activities | Snowfall box plot by class |
| BQ3 | Did El Niño winters have fewer very cold days? | Number of days with minimum temperature at or below −20°C; El Niño minus neutral difference | Describes whether severe cold remained common enough to matter in planning discussions | Cold-day comparison by class |
| BQ4 | Was the historical El Niño pattern different between southern and northern locations? | Compare each location's El Niño minus neutral differences, especially Windsor/Toronto versus Thunder Bay | Shows whether an Ontario-wide statement hides local variation | Station difference chart ordered by latitude, supported by a map |
| BQ5 | Did El Niño winters have fewer days with substantial new snowfall? | Number of days with at least 1 cm of new snow; El Niño minus neutral difference | Separates snowfall frequency from total accumulation | Snow-day comparison by class |
| BQ6 | Were differences larger during strong El Niño winters? | Strong El Niño minus neutral differences for temperature, snowfall and cold days; eligible winter counts | Tests whether the strong-event subset shows a different historical pattern | Strong-event comparison with confidence intervals and group sizes |

### Extended questions: impacts beyond the weather

Added after the core analysis to test whether the winter-weather differences reach activities that planners care about. They use the same winters, ENSO classes and bootstrap method.

| ID | Business question in simple English | KPI or comparison | Why the answer matters | Visual |
|---|---|---|---|---|
| BQ7 | Was heating demand lower in El Niño winters? | Heating-degree-days (K6); El Niño minus neutral, in HDD and % | A measured proxy for winter heating needs; not a bill or energy-use figure | `eda_heating_demand_by_city.png` |
| BQ8 | Do spring freeze-thaw conditions affect maple syrup production, and does El Niño change them? | Freeze-thaw days (K7) vs detrended maple production (K8); El Niño minus neutral freeze-thaw days | Maple sap flows on freeze-thaw days; tests whether El Niño reaches a winter-dependent industry | `eda_freeze_thaw_vs_maple.png` |
| BQ9 | Is the frost-free growing season longer after El Niño winters? | Growing-season length (K9); El Niño minus neutral | Context for agriculture and spring planning | `eda_growing_season_by_city.png` |
| BQ10 | Does El Niño show up in Ontario's economic growth? | Real GDP growth (K10); El Niño minus neutral | Scope check: whether a local weather effect is visible at provincial scale | `eda_gdp_growth_vs_enso.png` |

**Interpretation questions for every result:** How many usable winters support it? Does its uncertainty interval include zero? Does the pattern survive reasonable checks for the time period and long-term temperature trend?

## 4. Base KPI definitions

**Calculation grain:** one location × one winter. A winter is December through February, labelled by the year in which February falls. For example, December 1997–February 1998 has `winter_year = 1998`.

Calculate daily-to-winter metrics first. Then compare the winter summaries. This gives each eligible winter equal weight in its ENSO group.

| ID | KPI and output field | Definition / formula | Unit | Required inputs |
|---|---|---|---|---|
| K1 | Mean winter temperature: `mean_temp` | Sum of valid daily analysis means ÷ number of valid daily analysis means, after the declared temperature eligibility check | °C | `date`, daily mean temperature, location |
| K2 | Winter temperature anomaly: `temp_anomaly` | K1 for that winter − the location's baseline mean winter temperature | °C difference | K1 and the location's 1991–2020 winter baseline |
| K3 | Total winter snowfall: `snowfall_total_cm` | Sum of daily new snowfall across a complete winter | cm per winter | `date`, `snowfall_cm`, location |
| K4 | Snow days: `snow_days` | Count of winter dates with `snowfall_cm >= 1` | days per winter | `date`, `snowfall_cm`, location |
| K5 | Very cold days: `days_below_m20` | Count of winter dates with `tmin <= -20` | days per winter | `date`, `tmin`, location |

### Baseline definition for K2

Use eligible winters with `winter_year` from **1991 through 2020**, inclusive, and average their K1 values equally. Under this naming convention, the first baseline winter begins in December 1990. Document this convention so every script uses the same dates.

Calculate one fixed baseline per location. If fewer than 30 baseline winters qualify, disclose the actual count and describe it as an available-winter baseline average; do not claim a complete 30-winter normal. If no baseline winters qualify, withhold the anomaly.

A positive anomaly means warmer than the location's baseline. A negative anomaly means colder. Subtracting a fixed baseline does **not** remove a warming trend.

### Measurement distinctions

- Snowfall is newly fallen snow; it is not snow depth remaining on the ground.
- A snow day here means at least 1 cm of new snowfall, not a school closure or a snow-clearing deployment.
- Very cold days use measured minimum temperature, not wind chill.
- `rain_mm` and `precip_mm` support additional EDA but are not substitutes for `snowfall_cm` in these KPIs. Do not add centimetres of snow directly to millimetres of rain.
- In the supplied batch-cleaning outputs, use `tmean_analysis` for K1 when following that package's policy. `tmean` retains the cleaned observed mean; `tmean_derived` identifies calculated means.

### Impact KPIs (K6–K10)

| ID | KPI and output field | Definition / formula | Unit | Grain | Required inputs | Stored in |
|---|---|---|---|---|---|---|
| K6 | Heating-degree-days: `hdd_18` | (18 °C − K1) × expected winter days (90 or 91). Computed only for winters that pass the temperature rule. 18 °C is the Canadian standard base | °C-days per winter | location × winter | K1, `expected_days` | `result_heating_demand` |
| K7 | Sap-season freeze-thaw days: `freeze_thaw_days` | Count of dates from 1 February to 30 April with `tmin < 0` and `tmax > 0` on the same day. Requires complete `tmin` and `tmax` in every month (`freeze_thaw_pass`); otherwise missing | days per season | location × calendar year | `date`, `tmin`, `tmax` | `fact_sap_season` |
| K7p | Province-wide freeze-thaw days | Mean of K7 across the stations with a valid value that year | days per season | year | K7 | `result_maple_freeze_thaw` |
| K8 | Detrended maple production: `maple_residual` | Ontario maple syrup production minus its own linear trend fitted over all available years (1980–2025) | thousand gallons | year | Statistics Canada table 32-10-0354-01 | `result_maple_freeze_thaw` |
| K9 | Growing-season length: `growing_season_days` | Days from the last spring frost (last day on or before 30 June with `tmin <= 0`) to the first fall frost (first day on or after 1 July with `tmin <= 0`). Requires at least 355 valid `tmin` days in the year (`complete`); otherwise missing | days | location × calendar year | `date`, `tmin` | `fact_growing_season` |
| K10 | Real GDP growth: `gdp_growth_pct` | 100 × (this year's real GDP ÷ last year's − 1), chained 2017 dollars | % per year | year | Statistics Canada table 36-10-0222-01 | `fact_ontario_gdp` |

**Matching years to winters.** K7, K8, K9 and K10 are calendar-year measures. Year Y is matched to the ENSO class of `winter_year` Y, the winter whose February falls in year Y. For K7 and K8 this is the winter immediately before the sap season; for K9 and K10 it is the winter at the start of that year.

**Why detrend K8.** Ontario maple production grew strongly over the period as the industry expanded (more taps, tubing systems). Comparing raw production with weather would mostly measure that growth. The residual asks whether a year produced more or less than the trend would predict.

**Scope limits.** K6 is a demand proxy, not energy use or cost. Dollar translations of heating or snow-clearing effects are illustrative only and are not KPIs.

## 5. Comparison KPIs

For a location and metric, first calculate the arithmetic mean across eligible winters in each ENSO class. Count usable winters separately for every metric and class.

**Primary comparison formula:**

`difference = mean(metric in eligible El Niño winters) - mean(metric in eligible neutral winters)`

| ID | Comparison KPI | Unit | Interpretation |
|---|---|---|---|
| C1 | El Niño minus neutral mean temperature | °C | Positive: El Niño winters averaged warmer |
| C2 | El Niño minus neutral snowfall total | cm per winter | Negative: El Niño winters averaged less snowfall |
| C3 | El Niño minus neutral snow-day count | days per winter | Negative: El Niño winters averaged fewer snow days |
| C4 | El Niño minus neutral very-cold-day count | days per winter | Negative: El Niño winters averaged fewer very cold days |

Display La Niña group averages alongside El Niño and neutral results. For BQ6, repeat the same formulas with **strong El Niño** as the comparison group. Strong El Niño is a subset of El Niño, not a fourth mutually exclusive class.

For BQ4, compare these within-location differences across locations. A raw temperature difference between Toronto and Thunder Bay cannot by itself answer whether their ENSO associations differ. When station coverage periods differ, show those periods and repeat the geographic comparison on common eligible years where feasible. Do not label a few stations as a province-wide average.

**Illustrative example only:** if El Niño winters average −3.8°C and neutral winters average −5.0°C, C1 is +1.2°C. This explains the calculation; it is not a finding from this project.

### Impact comparisons (C5–C9)

| ID | Comparison | Formula | Unit | Stored in |
|---|---|---|---|---|
| C5 | Heating demand: El Niño minus neutral | Mean K6 in El Niño winters (including strong) − mean K6 in neutral winters; also as % of the neutral mean | HDD and % | `result_heating_demand` |
| C6 | Freeze-thaw vs maple production | Pearson correlation between K7p and K8 across years, with a bootstrap 95% interval (10,000 resamples of years) | r | `result_impact_tests` |
| C7 | Freeze-thaw days: El Niño minus neutral | Mean K7p in El Niño years − mean K7p in neutral years. **The caveat that travels with C6:** if its interval includes zero, the maple link cannot be attributed to El Niño | days | `result_impact_tests` |
| C8 | Growing season: El Niño minus neutral | Per station, and for the province-wide yearly average (years with at least 4 stations valid) | days | `result_growing_season` |
| C9 | GDP growth: El Niño minus neutral | Mean K10 in El Niño years − mean K10 in neutral years | percentage points | `result_impact_tests` |

C5–C9 use a fixed random seed (20260921) for every bootstrap, so reruns reproduce the same intervals.

## 5b. Supporting analysis metrics

These do not answer a business question on their own; they test how far the main results can be trusted.

| ID | Metric | Definition | Supports | Stored in |
|---|---|---|---|---|
| S1 | Warming trend | Least-squares slope of K2 against `winter_year`, per location, reported per decade | Timeline; trend check | `result_temperature_trends` |
| S2 | Trend-adjusted comparison | Repeat C1 using each winter's residual from the S1 trend line (`temp_detrended_residual`) instead of K2 | BQ1, BQ6: is the El Niño signal just recent warming? | `result_trend_sensitivity` |
| S3 | ENSO strength slope | Least-squares slope of K2 on the winter's DJF RONI value, per location, with a bootstrap 95% interval (5,000 resamples of winters) and Pearson r | BQ6: does a stronger El Niño mean a warmer winter? | `result_index_slopes` |
| S4 | North–south difference | (Thunder Bay − southern station) value per winter, then El Niño minus neutral of that difference, using only winters valid at both stations; southern stations: Windsor, Toronto | BQ4 | `result_regional_comparisons` |
| S5 | Index agreement | Share of comparisons whose verdict (interval excludes zero / inconclusive) is the same under ONI and RONI | Index choice | `result_enso_comparisons` (both indices) |
| S6 | Consistency of direction | Number of El Niño and strong El Niño comparisons pointing the expected way (warmer, less snow, fewer snow days, fewer cold days), and the number clearing zero, against the ~5% expected by chance | Overall pattern; multiple comparisons | Report, section 5 |

## 6. Reliability and data-quality indicators

These accompany the climate KPIs so readers can assess the evidence.

| Indicator | Calculation / definition | Reporting rule |
|---|---|---|
| Temperature coverage | 100 × valid daily analysis means ÷ expected winter days | Count absent calendar dates as missing; distinguish derived means from observations |
| Snowfall coverage | 100 × valid daily snowfall values ÷ expected winter days | Full snowfall totals and snow-day counts require complete daily coverage under the recommended rule below |
| Eligible winter count | Count of qualifying winters, separately by location, metric and ENSO class | Display group counts with every comparison |
| Derived/interpolated temperature share | 100 × estimated daily means used ÷ all valid daily means used | Report derivation and interpolation separately if both methods are used; denominator zero means unavailable |
| 95% confidence interval | Bootstrap the difference using 10,000 resamples of whole winters within each group; take the 2.5th and 97.5th percentiles | Save the random seed; report lower and upper bounds in the metric's units |

If the interval includes zero, describe the difference as **inconclusive**, not proof that there is no relationship. Empty or single-winter groups cannot support a meaningful bootstrap comparison; label them insufficient data. Very small groups remain uncertain even if a computed interval excludes zero. These intervals describe uncertainty in group differences, not a forecast range for next winter.

Do not count individual days as independent winters during resampling. If estimating uncertainty for a difference between locations, preserve shared winter-year relationships in the resampling.

## 7. Calculation rules and document differences

This file derives its questions and scope from the attached proposal. The repository README and previously supplied cleaner contain method changes that must be named explicitly in the final report.

| Decision | Attached proposal | Current repository README / supplied cleaner | **Final decision (used in all results)** |
|---|---|---|---|
| Main locations | Four; Sudbury is a backup | README adds Sudbury; cleaner processes all six available CSVs | **All six locations** |
| ENSO index | ONI | README specifies RONI; cleaner does not assign ENSO classes | **RONI primary; ONI repeated as a check (S5)** |
| Temperature completeness | At least 85 of 90 valid days; leap-winter interpretation is unspecified | Cleaner checks each month: no more than five missing days total and three consecutive missing days | **WMO "3 and 5" rule, applied to each month** |
| Missing daily mean | Proposal allows short linear interpolation | Cleaner derives a missing mean only from valid same-day maximum/minimum; no interpolation across dates | **Same-day (max + min) ÷ 2 only; no interpolation** |
| Snow and cold-day completeness | Snowfall is not filled, but total/count eligibility is not fully specified | Cleaner requires complete snowfall for K3/K4 and complete minimum temperature for K5 | **Complete daily data required for K3, K4, K5 and K7; never filled with zero** |

Under RONI, the strong El Niño winters (DJF RONI of +1.5 or more) are 1982–83, 1986–87, 1991–92, 1997–98 and 2015–16. The list is generated by the pipeline, not hardcoded.

**For summaries already produced by the cleaner**, honor its `temperature_pass`, `snowfall_pass`, and `cold_days_pass` fields. Describe them as that implementation's rules, not as an exact implementation of the attached proposal. If the team needs strict proposal replication, define its leap-year and interpolation rules and recalculate eligibility before publishing comparisons.

Recommended safeguard for totals and event counts: require all 90/91 days, or label the value incomplete and withhold the full-winter metric. Never convert missing snowfall to zero. ECCC's normals guidance distinguishes limited missingness for temperature averages from complete observations for totals and event counts. [ECCC calculation guidance, section 2.1](https://collaboration.cmc.ec.gc.ca/cmc/climate/Normals/Canadian_Climate_Normals_1991_2020_Calculation_Information.pdf)

For a proposal-based ONI analysis, use these study categories:

| Class | December–February index value |
|---|---|
| El Niño | At least +0.5 |
| Neutral | Greater than −0.5 and less than +0.5 |
| La Niña | At most −0.5 |
| Strong El Niño flag | At least +1.5 |

Store the index name, dataset version, source date and value. If using RONI instead, label the output accordingly and regenerate all classes and strong-winter lists. NOAA currently uses RONI for official monitoring; its event identification also considers persistence across overlapping seasons. This project's DJF threshold categories should be described as seasonal study categories. [NOAA index documentation](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/)

Do not hardcode the proposal's “about five strong winters.” Its example list omits winter 2009–10, which reaches the +1.5 cutoff in the current ONI table. Generate the list from the chosen index and then count usable winters separately for each KPI. [NOAA ONI table](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/)

## 8. Dashboard and reporting plan

| View | Content | Required context | Database source (views in `sql/dashboard_views.sql`) |
|---|---|---|---|
| Station map | Selected locations and average temperature anomaly for the chosen class | Location, index, actual years and eligible winter count | `v_dash_map` |
| ENSO comparison | C1–C4 by location, with confidence intervals | Metric units and sample sizes for both groups | `v_dash_comparison`, `v_dash_group_averages` |
| Historical timeline | Winter temperature anomalies by year, coloured by ENSO class, with a trend line | Baseline convention, station switches and gaps | `v_dash_timeline` |
| Impacts (optional) | C5–C9 | Proxy and attribution caveats (C6 with C7) | `v_dash_impacts`, `result_maple_freeze_thaw` |

Use separate panels for °C, centimetres and days. Show missing metrics as “Unavailable,” not zero. For a class-average dashboard card, average eligible winter-level values rather than summing temperatures or averaging all daily rows across winters.

The timeline displays long-term change; it does not adjust it away. As a supporting robustness check, compare results after accounting for calendar year or removing a fitted temperature trend. Report whether the interpretation changes.

Keep a comparison table with:

`city, metric, enso_index, comparison_group, reference_group, comparison_mean, reference_mean, difference, ci_lower, ci_upper, n_comparison, n_reference, eligible_years, quality_method`

## 9. What the final findings should say

Use this structure after calculations are complete:

> At [location], El Niño winters averaged [difference and unit] [warmer / less snowy / more snowy / fewer cold days] than neutral winters. The 95% confidence interval was [lower] to [upper], based on [N] El Niño and [N] neutral winters over [actual years]. [Explain whether the comparison is inconclusive and any coverage limitation.]

Do not fill these placeholders with assumptions or copy example findings from the proposal. Weather observations alone do not establish an amount of budget savings, an operational staffing target, or a forecast for 2026–27.

## 10. Completion checklist

Status as of September 26, 2026:

- [x] Included locations and ONI/RONI choice are consistent in the report and scripts (six locations, RONI primary). Dashboard: pending.
- [x] All winter KPIs use December–February and the same winter-year convention.
- [x] Each KPI has a declared completeness rule and missing values remain distinguishable from zero (NULL in the database).
- [x] The baseline period and number of qualifying baseline winters are documented (`result_city_baselines`).
- [x] Group comparisons include actual eligible years, group sizes and bootstrap confidence intervals.
- [x] Strong-winter membership is calculated from the chosen index.
- [x] Python and SQL reproduce the same eligible rows and summaries (`check_winter_summary.py`: 240 of 240 rows match).
- [x] Findings answer BQ1–BQ6 with uncertainty and local coverage limitations (`reports/findings.md`).
- [x] Findings answer BQ7–BQ10, with the attribution caveat on BQ8.
- [x] Recommendations stay within the weather evidence available.
- [ ] Dashboard built from the SQLite database.

## Source references

- User-provided proposal: `Ontario_ElNino_Proposal_and_4Week_Roadmap(2).md`, prepared September 18, 2026.
- [Repository daily CSV folder](https://github.com/KiranGill08/ontario-elnino-winters/tree/main/data/interim), checked September 21, 2026.
- [Repository README](https://github.com/KiranGill08/ontario-elnino-winters/blob/main/README.md), checked September 21, 2026; draft methods differ from the attached proposal.
- Statistics Canada, table 32-10-0354-01 (maple products) and table 36-10-0222-01 (gross domestic product, provincial and territorial).
- [NOAA ONI data and index documentation](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/).
- [ECCC 1991–2020 normals calculation guidance](https://collaboration.cmc.ec.gc.ca/cmc/climate/Normals/Canadian_Climate_Normals_1991_2020_Calculation_Information.pdf).
