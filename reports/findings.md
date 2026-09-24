# EDA scratch findings

Computed directly from `data/processed/*.csv` (RONI classification). Companion to the 5 charts in this folder. These are exploratory observations from a quick look at the data, not the project's reviewed results -- see `docs/validation.md` and `enso_comparisons.csv` for those.

## 1. Temperature anomaly by ENSO class (`eda_temp_anomaly_by_enso.png`)

At 6 of 6 stations, the El Nino median winter-temperature anomaly sits above the Neutral median. The boxes overlap substantially at every station -- winter-to-winter variability within an ENSO class is often as large as the shift between classes. Neutral is the smallest sample at every station (7-8 winters), so its box is the least stable of the three.

## 2. El Nino minus Neutral temperature, by station (`eda_el_nino_minus_neutral_by_station.png`)

All 6 stations show a positive difference (El Nino warmer than Neutral), from +0.75°C to +2.30°C. 0 of 6 individually clear the 95% bootstrap interval: none.

| Station | Difference (°C) | 95% interval | Status |
|---|---:|---|---|
| Windsor | +1.31 | -0.41 to 2.97 | inconclusive |
| London | +1.39 | -0.42 to 3.18 | inconclusive |
| Toronto Pearson | +1.29 | -0.52 to 2.96 | inconclusive |
| Ottawa | +0.75 | -1.09 to 2.41 | inconclusive |
| Sudbury | +1.75 | -0.18 to 3.50 | inconclusive |
| Thunder Bay | +2.30 | -0.01 to 4.65 | inconclusive |

## 3. Temperature anomaly timeline, 1982-2026 (`eda_temp_anomaly_timeline.png`)

Every station’s own linear trend line slopes upward across the 45-winter record:

| Station | °C per decade | Approx. total change, 1982-2026 |
|---|---:|---:|
| Windsor | +0.18 | +0.81 |
| London | +0.27 | +1.19 |
| Toronto Pearson | +0.48 | +2.09 |
| Ottawa | +0.27 | +1.17 |
| Sudbury | +0.15 | +0.66 |
| Thunder Bay | +0.33 | +1.46 |

El Nino winters (highlighted points) tend to sit at or above each city’s trend line rather than scattered randomly around it -- consistent with El Nino adding a further warm signal on top of the long-run trend, though this chart does not test that statistically.

## 4. Total snowfall by ENSO class (`eda_snowfall_by_enso.png`)

At 6 of 6 stations, the El Nino median total snowfall is lower than the Neutral median -- same direction as the temperature result. Snowfall records end earlier than temperature records at several stations (last usable winter: Windsor 2014; London 2003; Toronto Pearson 2026; Ottawa 2026; Sudbury 2022; Thunder Bay 2003). Thunder Bay in particular has far fewer usable winters than the others, so treat those boxes as less reliable.

## 5. Very cold days (below -20°C) by ENSO class (`eda_cold_days_by_enso.png`)

At 6 of 6 stations, El Nino winters average fewer very-cold days than Neutral winters. The effect size is dominated by latitude, not ENSO: Thunder Bay’s own El Nino mean (32.6 days) is close to Sudbury’s Neutral mean (31.3 days), even though El Nino is Thunder Bay’s mildest category -- the north-south climate gradient is larger than the within-city ENSO effect.

## Overall

Across all three El-Nino-vs-Neutral metrics checked here (temperature, snowfall, cold days), every one of the 6 stations points the same direction: warmer, less snow, fewer cold days in El Nino winters. Few individual station results clear statistical significance on their own, so the unanimous direction -- not any single station’s number -- is the strongest evidence in this dataset.