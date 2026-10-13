# Ontario Winters and El Niño

**Did El Niño winters in Ontario actually arrive warmer, less snowy and less extreme — and does the effect change from south to north?**

A six-station study of 45 winters (1981–82 to 2025–26), built as a complete analytics project: a reproducible Python pipeline, a SQLite star schema, a Power BI dashboard, a published findings report, and a deployed machine-learning service.

NOAA issued an El Niño advisory in August 2026 with a greater than 90% chance of a very strong El Niño through winter 2026-27. Ontario municipalities set winter maintenance budgets in the autumn. This project asks what 45 years of station records actually support — and, just as deliberately, what they do not.

> This is a historical analysis, not a forecast. It reports association, not causation.

---

## Headline results

| Finding | Evidence |
|---|---|
| **Strong El Niño winters were clearly warmer** | +2.4 to +4.1 °C above neutral winters at 5 of 6 stations, 95% intervals excluding zero |
| **The warming is a northern effect** | Thunder Bay +4.08 °C vs Toronto +2.37 °C. The difference between them is itself significant: **+1.20 °C, 95% CI [+0.20, +2.27]** |
| **Southern Ontario lost snow days** | Toronto −9.4 and Windsor −12.4 snow days in strong El Niño winters, both intervals excluding zero |
| **Extreme cold did not disappear** | Thunder Bay still recorded 17–33 days at or below −20 °C during strong El Niño winters |
| **Moderate El Niño winters are indistinguishable from any other winter** | Every all-El Niño temperature comparison is inconclusive at every station. The signal lives entirely in the 5 strong events |

The last two rows are the ones a planner needs most and the ones a headline would drop.

**Direction of effect:** all 48 El Niño comparisons point the same way — warmer, less snow, fewer snow days, fewer very cold days. 18 clear zero, against the 2–3 expected by chance.

---

## Business questions and KPIs

Each KPI is one location in one winter. A winter is December–February, named for the year February falls in.

| ID | Business question | KPI | Result |
|---|---|---|---|
| **BQ1** | Were El Niño winters warmer? | Mean winter temperature; anomaly vs the station's own 1991–2020 baseline | Yes for **strong** events (5 of 6 stations clear zero). Inconclusive for El Niño overall |
| **BQ2** | Did they bring less snow? | Total winter snowfall (cm) | Yes in the south (Windsor −61 cm, London −52 cm, Toronto −30 cm). Inconclusive in the north |
| **BQ3** | Were there fewer very cold days? | Days with minimum ≤ −20 °C | Fewer, most clearly Thunder Bay (−16.2 days). Never zero |
| **BQ4** | Does the effect differ south to north? | Paired difference-of-differences between station pairs | **Yes** — Thunder Bay's effect significantly exceeds Toronto's |
| **BQ5** | Fewer days with substantial new snow? | Days with ≥ 1 cm new snow | Yes in the south, inconclusive in the north |
| **BQ6** | Are strong events different? | All of the above, strong subset | **This is where the entire signal is** |

Full definitions: [`docs/kpis_and_business_questions.md`](docs/kpis_and_business_questions.md). Full results: [`reports/findings.md`](reports/findings.md).

### Temperature anomaly, strong El Niño minus neutral (RONI)

Stations ordered south to north.

| Station | Latitude | Difference | 95% CI | Verdict |
|---|---|---|---|---|
| Windsor | 42.28°N | +2.57 °C | [+0.78, +4.34] | clears zero |
| London | 43.03°N | +2.58 °C | [+0.65, +4.40] | clears zero |
| Toronto Pearson | 43.68°N | +2.37 °C | [+0.35, +4.23] | clears zero |
| Ottawa | 45.32°N | +1.41 °C | [−0.68, +3.37] | inconclusive |
| Sudbury | 46.63°N | +3.07 °C | [+1.05, +4.93] | clears zero |
| Thunder Bay | 48.37°N | **+4.08 °C** | [+1.87, +6.23] | clears zero |

Every difference carries a 10,000-sample bootstrap interval. Where an interval includes zero we call the result inconclusive and say so, rather than reporting the point estimate alone.

---

## What is in this repository

| Layer | Built with | Where |
|---|---|---|
| **Collection** | Python, ECCC bulk API, NOAA RONI/ONI | [`python/01_collection/`](python/01_collection) |
| **Cleaning** | pandas, WMO "3 and 5" completeness rule, full audit trail | [`python/02_cleaning/`](python/02_cleaning) |
| **Analysis** | Bootstrap confidence intervals, trend control, paired regional tests | [`python/03_analysis/`](python/03_analysis) |
| **Visualisation** | matplotlib, 17 charts with sample sizes and exclusions stated on every panel | [`python/04_eda/`](python/04_eda), [`reports/figures/`](reports/figures) |
| **Database** | SQLite star schema — `dim_city`, `fact_winter_kpis`, `result_*` | [`python/05_database/`](python/05_database), [`sql/`](sql) |
| **Dashboard** | Power BI, 5 pages | [`dashboard/`](dashboard) |
| **Machine learning** | scikit-learn, FastAPI, Docker | [`ml-winter-prediction/`](ml-winter-prediction) |
| **Reports** | Findings report, ML report, methodology, validation | [`reports/`](reports), [`docs/`](docs) |

One command reproduces every number:

```bash
python python/run_pipeline.py
```

It writes a timestamped folder under `runs/`, refuses to overwrite existing results, and records a `run_manifest.json` with SHA-256 hashes of every input, the library versions and every setting used.

---

## Data quality, stated up front

45 winters per station. These are how many are actually usable after the completeness rule — blank, never zero-filled.

| Station | Temperature | Snowfall | Cold days |
|---|---|---|---|
| Windsor | 39 / 45 | 31 / 45 | 37 / 45 |
| London | 44 / 45 | 20 / 45 | 41 / 45 |
| Toronto Pearson | 45 / 45 | 37 / 45 | 40 / 45 |
| Ottawa | 43 / 45 | 40 / 45 | 38 / 45 |
| Sudbury | 40 / 45 | 36 / 45 | 32 / 45 |
| Thunder Bay | 42 / 45 | **12 / 45** | 37 / 45 |

Thunder Bay reports snowfall in only 12 of 45 winters, which is why its snow results stay inconclusive while its temperature results are the strongest in the study. Zero-filling those gaps would have made Ontario look less snowy than it was, and the finding would have been an artifact of missing data.

Four candidate stations were tested and rejected, with reasons recorded rather than deleted — one had a five-year gap that swallowed the 2009-10 El Niño winter entirely.

---

## Machine learning: a model we recommend against deploying

[`ml-winter-prediction/`](ml-winter-prediction) asks whether this history can *anticipate* a mild winter before it starts. The honest answer is no, and the work is published because of that rather than in spite of it.

| Metric | Model | Do-nothing baseline |
|---|---|---|
| Accuracy | 68.4% | **69.2%** |
| Precision | 47.4% | — |
| ROC AUC | 0.609 | 0.500 |

**The model loses to assuming no winter is ever mild.** Two results make the exercise worth reading anyway:

- **Group leakage, measured.** Six stations share each winter and carry an identical ENSO value. Split rows at random and a random forest scores **0.87 AUC**; split by winter and the same model scores **0.55**. The ordinary evaluation would have shipped a model that does not work.
- **A boundary that cost a winter.** NOAA's thresholds are inclusive, so RONI +1.5 *is* a strong El Niño. `pd.cut`'s default excluded winter 1987 and made the strong band look like four winters instead of five. Caught by a unit test.

The model is served anyway — containerised, with `/predict` returning its own quality metrics and a guidance string stating it must not set budgets, and `/baseline` returning the historical rates that *are* defensible.

Full write-up: [`reports/ml_winter_prediction_report.md`](reports/ml_winter_prediction_report.md).

---

## Reproducibility

- **Validation gate.** `validate_results()` runs before any export: key uniqueness, row counts, calendar coverage, ENSO joins, baselines, anomalies and eligibility. The pipeline fails rather than writing unverified output.
- **Independent verification.** [`docs/validation.md`](docs/validation.md) records a line-by-line reconciliation of all 98,096 daily rows against source, recomputation of every KPI, and seven automated tests.
- **Fixed seeds.** Bootstrap seed and sample count are configuration, not defaults.
- **Single source of truth.** Every setting lives in [`python/config.py`](python/config.py). Changing the primary ENSO index from ONI to RONI is a one-line change that propagates through every table, chart and report.
- **API tests.** Nine tests cover the served model, including one asserting the project's central finding — that a strong El Niño scores higher in Thunder Bay than in Windsor.

---

## Limitations

Stated here rather than buried, because they decide how much weight the findings carry.

- **Five strong El Niño winters.** 1983, 1987, 1992, 1998 and 2016. Everything in the "strong" column rests on them. Five events cannot establish a rate.
- **Association, not cause.** The Arctic Oscillation and other drivers also act on Ontario winters.
- **Six stations stand in for a province.** The southwest is represented by Windsor and London only; nothing lies in the far north.
- **The index choice matters.** ONI and RONI disagree on 6 of 45 winters and on which count as strong. This project uses RONI, NOAA's official index since February 2026, and saves both.
- **Natural gas heating is not in the data**, so nothing here supports a claim about total energy use.

---

## Running it

```bash
pip install -r requirements.txt
python python/run_pipeline.py                      # full analysis, new runs/ folder
python python/05_database/load_database.py         # load that run into SQLite
```

The ML service:

```bash
cd ml-winter-prediction
docker build -t ontario-winter .
docker run --name winter-api -p 8000:8000 ontario-winter
```

Then `http://127.0.0.1:8000/docs`. See [`ml-winter-prediction/readme.rst`](ml-winter-prediction/readme.rst).

---

## Data sources

| Dataset | Provider |
|---|---|
| Daily climate records (temperature, snowfall) | Environment and Climate Change Canada, Historical Climate Data |
| Relative Oceanic Niño Index (RONI) and ONI, DJF | NOAA Climate Prediction Center |
| Maple syrup production, Ontario GDP | Statistics Canada |

Station records are joined across multiple ECCC station IDs per location, documented in [`data/raw/stations.csv`](data/raw/stations.csv) — every Ontario city in this study is really two or more weather stations over time.

---

## Team

| Contributor | Focus |
|---|---|
| **Kiran Gill** | Project lead, data collection, ENSO index definition and the switch to RONI, visual rebuild |
| **Ashish Sachdev** | Data cleaning and quality framework, KPI calculation, figures and reports |
| **Kumari** | Power BI dashboard |
| **Samir Omer** | Project scaffold and roadmap, machine learning and model deployment |

