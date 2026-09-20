# ontario-elnino-winters
# Ontario Winters and El Niño

A four-station analysis of how past El Niño winters looked in Ontario, from south to north.

> **How to use this template:** replace everything in [square brackets]. Write the sections marked **(Day 1)** at the start of the project, and the sections marked **(at the end)** once your results are final. Delete this note and any guidance lines when you're done.

---

## 1. Question (Day 1)

**Were El Niño winters in Ontario warmer, less snowy, or less extreme than other winters, and does the effect change from south to north?**

A very strong El Niño is developing for winter 2026-27. Before it arrives, this project looks back at about 45 winters (1981-82 to 2025-26) at four Ontario stations to see what El Niño winters actually looked like here.

This is a **historical analysis, not a forecast**. It shows associations with El Niño, not proof that El Niño caused them.

## 2. Key findings (at the end)

[Write 3 to 5 short findings, each with its uncertainty. Do not write these until your analysis is finished.]

Example format:
- [At Thunder Bay, El Niño winters averaged X °C warmer than neutral winters (95% confidence interval: X to X), based on N winters.]
- [Snowfall differences were inconclusive at most stations, because the confidence intervals include zero.]
- [The south-to-north pattern was / was not consistent across stations.]

If a result is small or uncertain, say so plainly. That is a valid finding.

## 3. Stations (Day 1)

| Region | Station | Station ID(s) | Climate ID | Years used | Notes |
|---|---|---|---|---|---|
| Southwest | [Windsor A] | [ID] | [ID] | [1981-2026] | [any gaps] |
| East | [Ottawa Macdonald-Cartier Int'l A] | [ID] | [ID] | [ ] | [ ] |
| Northeast | [Sudbury A] | [ID] | [ID] | [ ] | [ ] |
| Northwest | [Thunder Bay A] | [ID] | [ID] | [ ] | [ ] |

**Why these stations:** [Complete winter records, snowfall reported, and coverage of different parts of Ontario.]

**Why not Toronto:** [Its record is split across two stations (Toronto Lester B. Pearson Int'l A and Toronto Intl A), which need stitching, and it sits between Windsor and Ottawa. It can be added later as a fifth station.]

[If you used a station switch or replaced a station, describe it here, including the switch date.]

## 4. Data sources (Day 1, update as you go)

| Dataset | Provider | Used for | Downloaded on |
|---|---|---|---|
| Daily climate data (max, min, mean temperature; total snowfall) | Environment and Climate Change Canada, Historical Climate Data | Winter measures per station | [date] |
| Relative Oceanic Niño Index (RONI), DJF values | NOAA Climate Prediction Center | Labelling each winter El Niño, neutral, or La Niña | [date] |

**Links**
- ECCC Climate Data Extraction Tool (Daily climate data): https://climate-change.canada.ca/climate-data/#/daily-climate-data
- RONI text file: https://www.cpc.ncep.noaa.gov/data/indices/RONI.ascii.txt

**Index choice:** [State that you used RONI, NOAA's official ENSO index. Mention whether you compared with ONI.]

Raw files are kept unchanged in `data/raw/`. [Note which files, if any, are not included in the repository because of size.]

## 5. Method (at the end)

**Winter definition:** December, January, and February, named after the year in which February falls (December 1997 to February 1998 is winter "1997-98").

**ENSO classes** (using the December-February index value):

| Class | DJF value |
|---|---|
| El Niño | +0.5 or higher |
| Strong El Niño (subset) | +1.5 or higher |
| Neutral | between -0.5 and +0.5 |
| La Niña | -0.5 or lower |

**Measures per station, per winter**
- Mean winter temperature and its anomaly (difference from the station's 1991-2020 winter average)
- Total snowfall (cm) and snow days (days with at least 1 cm)
- Very cold days (minimum temperature at or below -20 °C)

**Data quality rule:** a station-winter is kept only if at least 85 of 90 days have valid temperature readings. Temperature gaps of up to 3 consecutive days are filled by linear interpolation and flagged. Missing snowfall is not filled. Dropped station-winters are listed in `[path to gap log]`.

**Comparison and uncertainty:** for each station, El Niño winters are compared with neutral winters. Every difference has a bootstrap 95% confidence interval (10,000 resamples of winters). If an interval includes zero, the result is described as inconclusive.

**Warming trend:** anomalies and a trend line are used so that long-term warming is not mistaken for an El Niño effect.

## 6. Results (at the end)

[Insert your main charts here.]

```
![Temperature anomaly by ENSO class](reports/figures/temp_anomaly_boxplot.png)
![El Niño minus neutral difference by station](reports/figures/difference_by_station.png)
```

[Add one sentence under each chart saying what it shows and how certain it is.]

Dashboard: [link or screenshot, if you built one]
Full report: [link to `reports/report.pdf`]

## 7. Limitations (at the end)

- Only about [5] strong El Niño winters exist in the study period, so results for "strong" events are uncertain.
- The list of strong winters depends on the index used (RONI or ONI).
- [Station records have gaps or station changes, described in section 3.]
- Ontario's El Niño signal is naturally weaker than in western Canada, so differences may be small.
- The analysis shows association, not cause. Other factors, such as the Arctic Oscillation, also affect Ontario winters.
- Natural gas heating is not captured, so the results say nothing about total energy use.

## 8. How to rerun this project (update as you build)

**Requirements:** Python 3.11 or newer.

```bash
git clone [your repository URL]
cd ontario-elnino-winters
pip install -r requirements.txt
```

**Steps** (update to match your actual scripts and notebooks)
1. Edit `config/stations.csv` if you want to change stations.
2. Download the data: `python src/[download script].py`
3. Run the notebooks in order:
   1. `notebooks/01_[name].ipynb`: load and clean
   2. `notebooks/02_[name].ipynb`: four stations and SQL
   3. `notebooks/03_[name].ipynb`: charts and findings
4. Outputs appear in `data/processed/`, `reports/`, and the SQLite database `[path]`.

## 9. Project structure

```
ontario-elnino-winters/
  config/stations.csv
  data/raw/            downloaded files, unchanged
  data/processed/      cleaned tables
  sql/                 SQL queries
  notebooks/           analysis notebooks
  src/                 reusable Python code
  dashboard/           dashboard files
  reports/             report and figures
  README.md
  requirements.txt
```

## 10. Data licence and credits

- Climate observations: Environment and Climate Change Canada. [Check the licence terms on the data page and state them here.]
- ENSO index: NOAA Climate Prediction Center. [Check and state the terms.]
- Author: [your name] · [contact or GitHub profile]

## 11. Status

- [ ] Stations chosen and data downloaded
- [ ] Data cleaned and gap log written
- [ ] Winter summary table (pandas and SQL match)
- [ ] Charts finished
- [ ] Confidence intervals added
- [ ] Report written
- [ ] README completed
