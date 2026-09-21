# Implemented methodology and decisions

## Purpose

Describe how historical Ontario winters differ between seasonal El Niño, neutral and La Niña categories. The five KPIs measure winter temperature, temperature anomaly, snowfall, snow days and very cold days. The comparison tables address ENSO contrasts, strong events and differences between selected northern and southern cities. These are historical associations, not forecasts or estimates of operational savings.

## Inputs and scope

The six daily CSVs were checked against the files in the [project's interim folder](https://github.com/KiranGill08/ontario-elnino-winters/tree/main/data/interim) on September 21, 2026. Their hashes appear in `results/run_manifest.json`; unchanged source copies are bundled under `data/raw/`. The snapshot contains 98,096 rows across London, Ottawa, Sudbury, Thunder Bay, Toronto and Windsor, spanning calendar dates in 1981–2026.

The original proposal selects Windsor, Toronto, Ottawa and Thunder Bay. The repository study also includes Sudbury. London is retained as an additional candidate because its CSV contains usable data; a prose claim of no observations is not sufficient to discard the supplied file. Inclusion flags allow either study scope to be selected explicitly. The included charts display all six candidates.

Analysis covers 45 DJF winters ending 1982–2026: December 1981 through February 2026, selecting only December, January and February within each season. January–February 1981 remain in the daily export but cannot form a complete winter without December 1980. Autumn 2026 and other non-study daily rows are retained without winter KPIs.

## Cleaning

The scripts validate the eight expected source columns, parse dates and numbers, normalize known missing markers, screen temperatures outside −50°C to 45°C, withhold inconsistent temperatures and negative precipitation, and retain an audit trail. Screening bounds are review rules, not proof that every remaining value is correct. Identical normalized duplicates retain one copy; conflicting same-date records and unusable date/station identifiers are quarantined for review.

In this snapshot, all 98,096 rows remain and no duplicate/date/negative-precipitation/temperature-screen failures were found. Three missing observed means can be estimated from valid same-day minimum and maximum values: Ottawa has two and Toronto has one. `tmean` remains the original observation; `tmean_analysis` holds the value used and `tmean_derived` flags the estimate. No measurements are interpolated across dates and no snowfall gaps are converted to zero.

The eight-column source has no original trace or quality-flag fields. The pipeline cannot recover trace distinctions or verify them from these CSVs. It also cannot resolve station moves or homogenize historical series merely from station IDs; station coverage reports make those IDs available for review.

## Eligibility and KPIs

The implemented temperature rule matches the previously supplied batch cleaner: each winter month must have at most five missing daily analysis means and no run longer than three missing days. Absent calendar dates count as missing. A winter passes only if all three months pass, then K1 averages its available valid daily analysis means.

This differs from the proposal's draft 85-of-90 eligibility and short-gap interpolation. It is recorded explicitly so results are not mistaken for calculations under that earlier rule. The monthly missing-day pattern and complete-total approach follow the concepts in [ECCC's 1991–2020 calculation information](https://collaboration.cmc.ec.gc.ca/cmc/climate/Normals/Canadian_Climate_Normals_1991_2020_Calculation_Information.pdf), but this project does not reproduce an official climate normal.

K3 and K4 require valid snowfall on all 90/91 expected days. K5 requires valid minima on all expected days. Snow days include snowfall ≥1 cm; very cold days include minimum temperatures ≤−20°C. A failed metric is blank, while independently eligible metrics remain available. Counts are not extrapolated and incomplete snowfall sums are not labelled full-winter totals.

## Baseline and anomalies

For each city, average its eligible K1 values for winters ending **1991 through 2020**, weighting each winter equally. The first starts in December 1990. This project convention is a set of winter ending years, not the same date interval as all calendar observations from January 1991 to December 2020.

K2 subtracts this one fixed city baseline from every eligible study winter's K1, including winters before 1991 and after 2020. A city with fewer than 30 eligible baseline winters gets a flagged available-winter baseline; no excluded winter is filled in. These partial baselines can affect comparisons between cities.

| City | Eligible baseline winters | Baseline mean, °C |
|---|---:|---:|
| London | 29 | −4.079379 |
| Ottawa | 28 | −7.823253 |
| Sudbury | 29 | −10.537800 |
| Thunder Bay | 27 | −11.533370 |
| Toronto Pearson | 30 | −3.590392 |
| Windsor | 25 | −2.208233 |

Within one city, subtracting a constant baseline does not change the El Niño-minus-neutral temperature difference. Thus K1 and K2 group differences have the same numerical value; they answer the question on different reference scales.

## ENSO assignment

ONI is primary to match the proposal. RONI is supplied as a parallel analysis because the repository README uses it. The package archives NOAA's [ONI ERSSTv6 table](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/) and [RONI table](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/), retrieved September 21, 2026. `enso_sources.json` records URLs and hashes. Reruns use the frozen CSV, so later revisions cannot silently change the results.

Classify each winter's published, one-decimal DJF value: ≥0.5 El Niño; ≤−0.5 La Niña; otherwise neutral. Strong El Niño means ≥1.5 and is a subset of El Niño. These are project seasonal categories, not a reconstruction of NOAA's operational persistence-based event declarations. Published rounding can matter at a category boundary.

Compute category lists from the input, not a draft list in prose. For example, winter ending 2010 has ONI 1.5 and RONI 1.4 in this snapshot, so only ONI classifies it as strong.

## Comparisons, uncertainty and regional question

For every city, index and KPI, compare eligible winters for El Niño minus neutral, strong El Niño minus neutral, El Niño minus La Niña, and La Niña minus neutral. Each winter gets equal weight within its group. Eligibility is metric-specific; sample sizes and winter lists are included in the output.

Resample whole winters independently within each compared group 10,000 times and take the 2.5th and 97.5th percentiles of the difference in means. A fixed seed and group-specific seed derivation make reruns reproducible. The procedure assumes winters are independent; it does not account for serial dependence, station-history changes or all possible confounding. Groups below ten eligible winters are marked as small. With fewer than two winters in either group, the confidence interval is withheld.

For the regional question, first match Thunder Bay to Windsor or Toronto on common eligible winter years, calculate a north-minus-south KPI difference for each matched winter, then compare those differences between El Niño and neutral winters. Resampling these paired winter differences preserves the same-winter city pairing. Conclusions apply to these selected station pairs, not Ontario as a whole.

Fit a simple linear temperature trend over eligible study winters at each city and repeat temperature comparisons on the residuals as a sensitivity check. These intervals condition on the estimated trend; they do not propagate fitting uncertainty. This check does not establish that ENSO caused a difference.

The many output intervals are exploratory and have no multiple-comparison correction. An interval excluding zero is not a guarantee of a stable future effect; an interval containing zero is inconclusive, not proof of no association. Missing snow records, small strong-event samples and baseline incompleteness must accompany interpretation.

## Reproduction

Run `python python/run_pipeline.py` from the package folder. It creates a new run directory and validates rows, keys, calendar coverage, joins and calculations before exporting. The manifest records settings, source hashes and software versions. Run `python -m unittest discover -s tests -v` for the focused edge-case checks. See `validation.md` for verification of the included output.
