ENSO is one of the most important climate phenomena on Earth due to its ability to change global atmospheric circulation, which influences temperature and precipitation across the globe. It has three states/phases:

1. El Nino / warm phase: the unusual warm ocean temperatures in the eastern Pacific
2. La Nina / cool phase: the unusual cool ocean temperatures in the eastern Pacific
3. Neutral: neither El Nino nor La Nina

# Ontario Winters and El Niño

A five-station analysis of how past El Niño winters looked in Ontario, from south to north.

> **How to use this file:** replace everything in [square brackets] with your own numbers once you have them. The station IDs below come from ECCC page addresses and station inventories, so confirm any marked **[confirm]** on ECCC's station pages. Delete this note when you're done.

---

## 1. Question

**Were El Niño winters in Ontario warmer, less snowy, or less extreme than other winters, and does the effect change from south to north?**

A very strong El Niño is developing for winter 2026-27. Before it arrives, this project looks back at winters from 1981-82 to 2025-26 at five Ontario stations to see what El Niño winters actually looked like here.

This is a **historical analysis, not a forecast**. It shows associations with El Niño, not proof that El Niño caused them.

## 2. Key findings (write these last)

[Write 3 to 5 short findings, each with its uncertainty. Do not write them until the analysis is finished.]

- [At Thunder Bay, El Niño winters averaged X °C warmer than neutral winters (95% confidence interval: X to X), based on N winters.]
- [Snowfall differences were inconclusive at most stations, because the confidence intervals include zero.]
- [The south-to-north pattern was / was not consistent across stations.]

## 3. Stations and station IDs

Environment and Climate Change Canada (ECCC) often splits one place into several station records over the years, each with its own **StationID** (used to download data) and **Climate ID** (the official identifier). Each station below therefore uses two records, joined together. **Where both records report the same day, the newer ID is kept.**

| Region | Station | Newer record: StationID (Climate ID) | Older record: StationID (Climate ID) |
|---|---|---|---|
| Southwest | Windsor A | 54738 ([Climate ID, confirm]) | 4716 (6139525) |
| South-central | Toronto Pearson | 51459 (6158731), Toronto Intl A | 5097 (6158733), Toronto Lester B. Pearson Int'l A |
| East | Ottawa Macdonald-Cartier | 49568 (6106001 **[confirm]**), Ottawa Intl A | 4337 (6106000), Ottawa Macdonald-Cartier Int'l A |
| Northeast | Sudbury A | 50840 (6068153) | 4132 (6068150) |
| Northwest | Thunder Bay | 30682 (6048268), Thunder Bay CS | 4055 (6048261), Thunder Bay A |

Approximate locations: Windsor 42.28°N, 82.96°W; Toronto Pearson 43.68°N, 79.63°W; Ottawa 45.32°N, 75.67°W; Sudbury 46.63°N, 80.80°W; Thunder Bay 48.37°N, 89.33°W. The same table, one row per ID, is in `config/stations.csv`.

**Where the records hand over** (fill in from the download summaries):

| Station | Older record ends | Newer record starts | Gap between them? | Snowfall usable through |
|---|---|---|---|---|
| Windsor | [ ] | [ ] | [ ] | about 2017-18 **[confirm]** |
| Toronto | about 2013 | about mid-2013 | [ ] | [ ] |
| Ottawa | about 2011 | [ ] | [ ] | [ ] |
| Sudbury | [ ] | about 2014 | [ ] | [ ] |
| Thunder Bay | about 2004 | about 2003-04 | [ ] | [ ] |

## 4. How the stations were chosen

Stations had to meet four tests: (1) most winters with complete daily temperature, (2) snowfall reported, (3) a clean or well-documented switch between old and new records, and (4) a spread across Ontario.

**Stations tested and not used**

| Station | IDs tested | Why it was not used |
|---|---|---|
| London | 4789 (6144475), 10999 (6144478), 50093 (6144473) | No daily data from about 2003 to 2012, which includes the strong El Niño winter 2009-10 |
| Geraldton | 4003, 53519, 54240, 54858 | No usable daily data after 2018; also an inland site close to Thunder Bay and Sudbury |
| Kingsville MOE | 4647 (6134190) | Only 24 of 45 winters passed the strict 85-of-90-day rule; overlaps Windsor's region |
| Welcome Island (AUT) | 4061 (6049443) | No temperature values for 1981-82 to 1995-96; only 18 of 45 winters usable **[confirm which station this was]** |

Lesson recorded here for anyone repeating this: the ECCC station inventory shows only the first and last year of daily data, not whether the years in between (or the recent years) actually contain usable values. Always download and check.

## 5. Data sources

| Dataset | Provider | Used for | Downloaded on |
|---|---|---|---|
| Daily climate data (max, min, mean temperature; total snowfall) | Environment and Climate Change Canada, Historical Climate Data | Winter measures per station | [date] |
| Relative Oceanic Niño Index (RONI), DJF values | NOAA Climate Prediction Center | Labelling each winter El Niño, neutral, or La Niña | [date] |
| Station inventory (`climate-stations.csv`) | Environment and Climate Change Canada | Finding station IDs and record years | [date; confirm source] |

**Links**
- ECCC Climate Data Extraction Tool (Daily climate data): https://climate-change.canada.ca/climate-data/#/daily-climate-data
- ECCC bulk daily download (one station-year per request): `https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=<ID>&Year=<YYYY>&Month=1&Day=1&timeframe=2&submit=Download+Data`
- RONI text file: https://www.cpc.ncep.noaa.gov/data/indices/RONI.ascii.txt
- ECCC station inventory folder: https://collaboration.cmc.ec.gc.ca/cmc/climate/Get_More_Data_Plus_de_donnees/

**Index choice:** [State that you used RONI, NOAA's official ENSO index since February 2026, and whether you compared with ONI. The list of strong winters depends on the index.]

## 6. How the data were collected

Yearly files for each station ID are saved unchanged in `data/raw/<station>/`, then combined into one daily table per station in `data/processed/<station>_daily.csv`.

```bash
python download_station.py windsor 54738 4716
python download_station.py toronto 51459 5097
python download_station.py ottawa 49568 4337
python download_station.py sudbury 50840 4132
python download_station.py thunderbay 30682 4055
```

List the newer ID first. The script tests one download, fetches every year from 1981 to 2026 for each ID, and prints a summary showing each ID's date range and how complete temperature and snowfall are.

**Helper scripts used to choose stations**
- `find_stations.py`: searches the station inventory by name or location
- `screen_stations.py`: tests several single-ID candidates at once
- `probe_station.py`: shows which years each ID really supplies, with about a dozen downloads
- `compare_stations.py`: compares all saved station files in one table

## 7. Method

**Winter definition:** December, January, and February, named after the year in which February falls (December 1997 to February 1998 is winter "1997-98").

**ENSO classes** (using the December-February index value):

| Class | DJF value |
|---|---|
| El Niño | +0.5 or higher |
| Strong El Niño (subset) | +1.5 or higher |
| Neutral | between -0.5 and +0.5 |
| La Niña | -0.5 or lower |

**Strong El Niño winters** in both ONI and RONI: 1982-83, 1991-92, 1997-98, 2009-10, and 2015-16. [Note that 2023-24 is strong in ONI but not RONI, and 1986-87 the reverse. Recheck against the current files, since 2009-10 sits right on the +1.5 cutoff.]

**Measures per station, per winter**
- Mean winter temperature and its anomaly (difference from the station's 1991-2020 winter average)
- Total snowfall (cm) and snow days (days with at least 1 cm)
- Very cold days (minimum temperature at or below -20 °C)

**Data quality rule:** a winter is used for a measure only if it passes the WMO "3 and 5" rule in each of December, January, and February: no more than 3 consecutive and no more than 5 total missing days per month. This is the rule ECCC uses for climate normals. When the daily mean temperature is missing but the maximum and minimum exist, the mean is taken as (max + min) / 2. Snowfall gaps are not filled, because a blank normally means "not observed", not zero. [If you used the stricter 85-of-90-day rule for any station, say so here.]

**Comparison and uncertainty:** for each station, El Niño winters are compared with neutral winters. Every difference has a bootstrap 95% confidence interval (10,000 resamples of winters). If an interval includes zero, the result is called inconclusive.

**Warming trend:** anomalies and a trend line are used so long-term warming is not mistaken for an El Niño effect.

## 8. Data quality by station (fill from `compare_stations.py`)

| Station | Winters passing (temperature) | Winters passing (snowfall) | Last complete snowfall winter | Strong winters usable (temp / snow, out of 5) |
|---|---|---|---|---|
| Windsor | [ ] | [ ] | [ ] | [ ] |
| Toronto | [ ] | [ ] | [ ] | [ ] |
| Ottawa | [ ] | [ ] | [ ] | [ ] |
| Sudbury | [ ] | [ ] | [ ] | [ ] |
| Thunder Bay | [ ] | [ ] | [ ] | [ ] |

## 9. Results (write these last)

[Insert your main charts here.]

```
![Temperature anomaly by ENSO class](reports/figures/temp_anomaly_boxplot.png)
![El Niño minus neutral difference by station](reports/figures/difference_by_station.png)
```

[Add one sentence under each chart saying what it shows and how certain it is.]

## 10. Limitations

- Only about five strong El Niño winters exist in the study period, so results for "strong" events are uncertain.
- The list of strong winters depends on the index used (RONI or ONI).
- Every station joins two ECCC records, so a small shift in readings at the switch date is possible. [Add any comparison you made on overlapping days.]
- **Windsor's rain and snow are missing after about 2018.** Windsor is used for temperature through 2025-26 but for snowfall only through about 2017-18. All five strong El Niño winters fall in that period. [Add similar notes for any other station whose snowfall ends early.]
- Snowfall periods differ between stations, so snowfall comparisons across stations cover different years. Comparisons are made within each station first.
- Ontario's El Niño signal is naturally weaker than in western Canada, so differences may be small.
- The analysis shows association, not cause. Other factors, such as the Arctic Oscillation, also affect Ontario winters.
- Natural gas heating is not captured, so the results say nothing about total energy use.
- Toronto stands in for southern Ontario's largest city, but the southwest is represented only by Windsor.

## 11. Project structure

```
ontario-elnino-winters/
  config/stations.csv      station IDs, one row per record
  climate-stations.csv     station inventory
  data/raw/<station>/      yearly files, unchanged (windsor, toronto, ottawa, sudbury, thunderbay)
  data/processed/          <station>_daily.csv, one per station
  notebooks/               analysis notebooks
  sql/                     SQL queries
  src/                     download and helper scripts
  reports/                 report and figures
  README.md
  requirements.txt
```

[Move the London, Geraldton, and Kingsville folders and files to an `excluded/` folder rather than deleting them, so the reasons in section 4 stay reproducible.]

## 12. How to rerun

**Requirements:** Python 3.11 or newer.

```bash
git clone [your repository URL]
cd ontario-elnino-winters
pip install -r requirements.txt
```

1. Run the five download commands in section 6.
2. Run `python compare_stations.py` and check the table matches section 8.
3. Run the notebooks in order: `notebooks/01_[name].ipynb`, `02_[name].ipynb`, `03_[name].ipynb`.

## 13. Data licence and credits

- Climate observations: Environment and Climate Change Canada. [Check the licence terms on the data page and state them here.]
- ENSO index: NOAA Climate Prediction Center. [Check and state the terms.]
- Author: [your name] · [contact or GitHub profile]

## 14. Status

- [x] Stations chosen and station IDs recorded
- [ ] All five stations downloaded and combined
- [ ] Completeness table (section 8) filled in
- [ ] Winter summary table (pandas and SQL match)
- [ ] Charts finished
- [ ] Confidence intervals added
- [ ] Report written
- [ ] README completed
