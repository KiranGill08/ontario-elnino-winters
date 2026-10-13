# Can We Anticipate a Mild Ontario Winter? A Predictive Modelling Report

**Study period:** winters 1981–82 to 2025–26 · **Stations:** Windsor, London, Toronto Pearson, Ottawa, Sudbury, Thunder Bay · **Primary ENSO index:** RONI · **Prepared:** October 2026 · **Author:** Samir Omer

Companion to [`findings.md`](findings.md). That report describes what past El Niño winters *looked like*. This one asks whether that history is strong enough to **anticipate** a winter before it begins, and reports that it is not.

Code and notebooks: [`../ml-winter-prediction/`](../ml-winter-prediction).

## Summary

- **The model does not work, and that is the result.** Out-of-fold accuracy is **68.4%** against **69.2%** for assuming no winter is ever mild. It loses to doing nothing.
- **Its ranking is weak but real.** ROC AUC 0.609. The ordering carries some information; the yes/no labels at a 0.5 threshold throw it away.
- **Precision is 47.4%.** When the model calls a winter mild it is wrong more often than right — not a basis for reducing a salt budget.
- **The evaluation method mattered more than the model.** Splitting rows at random inflates a random forest from **0.55 to 0.87 AUC**. Six stations share each winter and carry an identical ENSO value, so a conventional split tests the model on winters it has already seen. Without group-aware splitting this report would be recommending a model that does not work.
- **What the base rates do support:** roughly **seven in ten** location-winters during the five strong El Niño events came in at least 1 °C above the station's baseline, against a 31% overall rate. The effect rises with latitude.
- **The relationship is a step, not a slope.** Moderate El Niño winters were mild *less* often than neutral winters. Nothing happens until the index clears +1.5.
- **A mild winter is not a winter without cold snaps.** Thunder Bay still recorded 17 to 33 days at or below −20 °C during those same strong El Niño winters.

## 1. Question and framing

**Before a winter begins, can we tell an Ontario municipality it is heading for a mild winter, so that salt, plough and overtime budgets can be set with better information than last year's figure?**

Municipal winter budgets are set in the autumn. NOAA issued an El Niño advisory in August 2026 with better than 90% confidence of a very strong El Niño for winter 2026-27. If 45 years of Ontario station records support a planning adjustment, this is the year it would matter.

**Target KPI:** share of winters correctly anticipated as mild, measured against what a planner gets by assuming every winter will be normal. That comparison — against the do-nothing option — is the test the model has to pass, and it is the test it fails.

## 2. Data and target

Built from the project's own pipeline output, `data/processed/winter_kpis.csv`. Nothing is synthetic.

| | |
|---|---|
| Grain | One location in one winter |
| Rows after eligibility rules | 253 of 270 |
| Rows after the lagged feature | **247**, across **44 distinct winters** |
| Target | `Mild_Winter` — at least **1.0 °C** above that location's own 1991–2020 baseline |
| Base rate | **30.8%** |

**Why temperature and not snow.** Snowfall is usable in only 176 of 270 location-winters, and at Thunder Bay in just 12 of 45. A snow-burden target — closer to what a maintenance budget actually tracks — would have been modelled almost entirely on the south. Temperature is the best-measured variable in the dataset. This is a constraint imposed by data quality, not a preference.

**Why +1.0 °C.** Splitting at zero would place a winter 0.1 °C above normal in the same class as one 3 °C above it, and would produce a near 50/50 target that is mostly noise around the threshold. A full degree above a thirty-year normal is a winter a planner notices. It also preserves a 31% base rate, which is what makes the accuracy comparison in section 5 meaningful.

## 3. Features

Only what a planner could hold in October.

| Feature | Source | Rationale |
|---|---|---|
| `ENSO_Value` | RONI DJF | The driver the project is about |
| `ENSO_Strength` | `abs(ENSO_Value)` | Separates magnitude from direction, so the model is not forced to assume −2.0 does the opposite of +2.0 |
| `ENSO_x_Latitude` | Product with centred latitude | Encodes BQ4 directly: a linear model cannot learn "El Niño does more in the north" from the two columns separately |
| `latitude_approx`, `baseline_mean_temp` | Station reference | Fixed station properties |
| `winter_year` | — | Long-term trend |
| `Prev_Anomaly` | Lag 1 at the same location | Last winter has finished, so it is legitimately known |
| `ENSO_Class`, `city_name` | Categorical | One-hot encoded inside the pipeline |

**Excluded as leakage:** `temp_anomaly` (the target before thresholding), `mean_temp` (the target in another form), and `snowfall_total_cm` and `days_below_m20`, both measured *during* the winter being predicted.

### The honest problem with the ENSO feature

The project labels each winter with its **December–February** index value. That number does not exist until the winter is over; a planner in October has a forecast of it instead, carrying forecast error.

The model is therefore given the actual outcome of the ENSO season and asked about the weather that accompanied it. **Every score in this report is an upper bound** on what a deployed version could achieve. Dropping the feature would remove the only variable the project exists to study, so it is retained and the limitation is stated instead.

## 4. Method

**Model:** logistic regression inside a scikit-learn `Pipeline` that standardises and one-hot encodes on training data only.

**Chosen because** 44 independent winters cannot support anything more flexible, and because the business needs a probability it can explain to a council rather than a black box. Under group-aware cross-validation it was also the only candidate meaningfully above chance:

| Model | AUC, rows split at random | AUC, split by winter | Overstated by |
|---|---|---|---|
| Logistic Regression | 0.691 | **0.690** | +0.001 |
| Decision Tree | 0.803 | 0.435 | +0.368 |
| Random Forest | 0.873 | 0.548 | +0.325 |

**Evaluation:** `GroupKFold` on `winter_year`, pooling out-of-fold predictions so all 247 rows are scored by a model that never saw their winter. A single hold-out of 11 winters produced AUCs between 0.344 and 0.767 across eleven seeds (mean 0.579, standard deviation 0.140) — far too unstable to quote.

## 5. Results

| Metric | Model | Do-nothing baseline |
|---|---|---|
| Accuracy | **68.4%** | **69.2%** |
| Precision | 47.4% | — |
| Recall | 23.7% | 0% |
| F1 | 0.316 | — |
| ROC AUC | **0.609** | 0.500 |

Confusion matrix, out-of-fold, 247 location-winters:

| | Predicted not mild | Predicted mild |
|---|---|---|
| **Actually not mild** | 151 | 20 |
| **Actually mild** | 58 | 18 |

**Accuracy is the wrong verdict metric here, in both directions.** Both figures sit near 69% because 69% of winters are not mild — so accuracy would have *undersold* a model whose ranking (AUC 0.609) does carry information, while also failing to show that the labels are useless. Neither fact is visible from accuracy alone.

### What the base rates support, where the model does not

| ENSO band | Location-winters | Distinct winters | Mild rate |
|---|---|---|---|
| Strong La Niña | 24 | 4 | 25.0% |
| La Niña | 91 | 16 | 30.8% |
| Neutral | 46 | 8 | 26.1% |
| El Niño | 57 | 11 | **17.5%** |
| **Strong El Niño** | 29 | **5** | **69.0%** |

Moderate El Niño winters were mild *less* often than neutral winters. The association is a step at +1.5, not a slope — so "an El Niño is coming" carries no information on this record, while "a *strong* El Niño is coming" does.

### Where the effect lands

El Niño minus other winters, mild-rate difference, ordered south to north:

| Station | Latitude | Difference |
|---|---|---|
| Windsor | 42.28°N | −10 pts |
| London | 43.03°N | −2 pts |
| Toronto Pearson | 43.68°N | −7 pts |
| Ottawa | 45.32°N | +10 pts |
| Sudbury | 46.63°N | +22 pts |
| Thunder Bay | 48.37°N | +24 pts |

Winter 1987 shows the whole pattern in a single season. Same ocean, same index value of exactly +1.5: Thunder Bay finished **3.6 °C** above its baseline and Sudbury 1.9 °C above, while Toronto finished slightly *below* and Windsor and London barely moved. A single province-wide figure for that winter would report about half a degree above normal and describe none of those six places.

## 6. Two findings about method

**6.1 Group leakage, quantified.** Six stations observe the same 44 winters, and the ENSO value is identical across all six rows of a winter. A random row split puts Toronto's 2016 in training and Ottawa's 2016 in test — the model has already been shown the answer. Measured cost: a random forest reports 0.873 AUC under the conventional split and 0.548 under the honest one. Logistic regression barely moves, because it never had the capacity to memorise winters. The flexible models had the most to gain from the shortcut and lost the most when it closed.

**6.2 A boundary condition that cost a winter.** NOAA's ENSO thresholds are inclusive: an index of exactly +1.5 *is* a strong El Niño. `pandas.cut` defaults to `right=True`, making the top band `(1.5, ∞]`. Winter 1987 sits at exactly RONI +1.5 and was silently dropped, making the strong band appear to hold four winters instead of five and shifting its mild rate from 69% to 78%. Caught by an API unit test asserting the documented count, and fixed by writing the banding out explicitly rather than relying on a library default.

## 7. Deployment

The model is containerised and served with FastAPI ([`../ml-winter-prediction/`](../ml-winter-prediction)) — deliberately, despite the negative result. A model published with its evaluation attached can be argued with; one that exists only as a notebook claim cannot.

| Endpoint | Returns |
|---|---|
| `POST /predict` | Mild probability, the historical rate for that ENSO band, the model's own quality metrics, and a guidance string stating it must not set budgets |
| `GET /baseline` | The historical rates in section 5 — the defensible output |
| `GET /model-card` | Task, training data, evaluation method, metrics, and limitations in full |

Nine tests cover the service, including one asserting that a strong El Niño scores higher at Thunder Bay than at Windsor, so the project's central finding is a regression test.

## 8. Recommendations

1. **Do not use the model for budgeting.** It does not beat the assumption it would replace. Every other recommendation is secondary to this one.
2. **Use the strong-El Niño base rate as a planning prior, in the north only.** For Sudbury, Thunder Bay and comparable northern stations, a confirmed strong El Niño is weak evidence to lean toward the milder end of an existing planning range. It is not grounds for a new range. For Windsor, London and Toronto the record supports no adjustment.
3. **Never reduce cold-snap provision.** Thunder Bay recorded 17 to 33 days at or below −20 °C during the strong El Niño winters, against an all-winter median of 37. Mild in the seasonal average is not mild in the tail, and the tail is what the emergency budget exists for.
4. **State the 2026-27 outlook precisely.** The defensible sentence is: *"If it verifies as strong, northern Ontario has historically leaned mild — on five prior events. Southern Ontario has not. Keep cold-snap reserves regardless."* Anything more specific is not supported.
5. **Measure winter 2026-27 the same way.** A sixth strong event is worth more to this analysis than any further modelling of the existing five. This is the highest-value action available to the project.

## 9. Limitations

**The binding constraint is five winters.** 1983, 1987, 1992, 1998 and 2016. Every usable statement here rests on them. Five events cannot establish a rate; they can only fail to contradict one.

| Limitation | Consequence |
|---|---|
| DJF index not known in advance | All scores are an upper bound on deployable skill |
| 247 rows but 44 independent winters | Effective sample for anything ENSO-related is 44; for strong events, five |
| Association, not cause | Other drivers also act on Ontario winters |
| Temperature target only | Snow burden, closer to what municipalities budget, is not supported by the data |
| Baseline overlaps the study period | For early winters the 1991–2020 reference partly postdates them |
| Six stations for a province | Southwest is Windsor and London only; nothing in the far north |
| A fixed +1.0 °C threshold | "Mild" is a definition. The latitude gradient holds across reasonable alternatives; the rates do not |

**What would improve this materially**, in order of value: more strong events (unavailable by definition — hence recommendation 5); snowfall coverage in the north, which would allow modelling the metric municipalities actually budget for; using NOAA's autumn forecast rather than the observed DJF value, for an honest estimate of deployable skill; and a wider station network, which would turn a six-point latitude gradient into something testable rather than suggestive.

## 10. Conclusion

A machine-learning model built on this data cannot tell an Ontario municipality whether an individual winter will be mild. It is less accurate than assuming none ever is, and its mild calls are wrong more often than right.

The record still contains something usable: during five strong El Niño events, roughly seven in ten location-winters came in at least 1 °C above normal, and the effect grew with latitude. That is a base rate for a planning conversation, not a prediction for a budget line.

The most transferable result in this report is methodological. The difference between 0.87 and 0.55 AUC was not a better model — it was asking the question honestly.
