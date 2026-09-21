# Project Proposal and 4-Week Roadmap

## Ontario Winters and El Niño: A Four-Station Analysis

**Prepared:** September 18, 2026
**Level:** Beginner to lower-intermediate
**Region:** Ontario, Canada (four weather stations)
**Season studied:** Winter (December to February)
**Duration:** 4 weeks (September 21 to October 18, 2026)
**Expected effort:** about 10 to 12 hours per week (roughly 40 to 48 hours in total)
**Budget:** $0 (all data and tools are free)

---

# PART A: PROPOSAL

## 1. Summary

NOAA's Climate Prediction Center issued an El Niño Advisory on August 13, 2026, and reported a greater than 90% chance of a very strong El Niño through fall and winter 2026-27. Forecasters expect a milder winter across much of Canada, but how strongly Ontario responds is less certain.

This project looks back at past winters. It compares El Niño, neutral, and La Niña winters at four Ontario stations, from south to north, to answer one question:

> **Were El Niño winters in Ontario warmer, less snowy, or less extreme than other winters, and does the effect change from south to north?**

The outputs are a cleaned dataset, a small SQL database, a set of clear charts with uncertainty ranges, a simple dashboard, and a short written report. The results provide historical context for the 2026-27 winter, but the project does not make a forecast.

## 2. Nature of the Analysis

- **Main method:** comparative (composite) analysis, comparing groups of winters by ENSO class.
- **Supporting methods:** descriptive statistics, time series (trend line), bootstrap confidence intervals, and a south-to-north geographic comparison.
- **Topic:** climate *variability* (natural year-to-year swings such as El Niño), not long-term climate *change*. The two overlap, because Ontario's winters have warmed over the decades, so anomalies and a trend line are used to keep the warming trend from being mistaken for an El Niño effect.
- **Not causal:** the project shows associations with El Niño, not proof that El Niño caused them. Other factors, such as the Arctic Oscillation, also affect Ontario winters.

## 3. Research Questions

1. Were El Niño winters warmer than neutral winters at each station?
2. Did total snowfall differ between El Niño winters and other winters?
3. Did the number of very cold days (minimum temperature at or below -20°C) change?
4. Does the effect differ between the south (Windsor, Toronto) and the north (Thunder Bay)?

## 4. Stations

| Region | Station | Why it was chosen |
|---|---|---|
| Southwest | Windsor A | Mildest winters, south of the province |
| Central | Toronto Pearson Intl A | Largest population, familiar reference |
| East | Ottawa Macdonald-Cartier Intl A | Eastern Ontario, colder and snowier than Toronto |
| Northwest | Thunder Bay A | Coldest and snowiest, strong north-south contrast |

**Before starting:** confirm the exact station ID, name, and years of data for each in Environment and Climate Change Canada's (ECCC) Historical Climate Data database, since stations are sometimes renamed or moved.

**Backup rule:** if a station has too many gaps or too short a record, replace Ottawa with Sudbury A, or drop it and continue with three. Decide this by the end of Week 2 and note it in the report.

## 5. Study Design

**Period:** winters 1981-82 to 2025-26 (about 45 winters). If a station starts later, use its available years.

**Defining a winter:** December, January, and February, named after the year in which February falls. December 1997 to February 1998 is winter "1997-98", stored as `winter_year = 1998`.

**Classifying winters by ENSO** using the December-February (DJF) ONI value from NOAA:

| Class | DJF ONI |
|---|---|
| El Niño | +0.5 or higher |
| Neutral | between -0.5 and +0.5 |
| La Niña | -0.5 or lower |

Mark **strong El Niño** winters (ONI at or above +1.5) as a subset. They are expected to be 1982-83, 1991-92, 1997-98, 2015-16, and 2023-24. Confirm this list against NOAA's official ONI table.

**Measures per station, per winter**
- Mean winter temperature and its anomaly (difference from that station's 1991-2020 winter average)
- Total snowfall (cm)
- Snow days (days with at least 1 cm of snow)
- Very cold days (minimum temperature at or below -20°C)

**Data quality rule:** keep a station-winter only if at least 85 of 90 days have valid temperature readings. Fill temperature gaps of up to 3 consecutive days by linear interpolation and flag them. Do not fill missing snowfall. Keep a log of every dropped station-winter and the reason.

## 6. Data Sources

| Dataset | Provider | Use |
|---|---|---|
| Historical Climate Data (daily) | Environment and Climate Change Canada | Daily max, min, and mean temperature and snowfall per station |
| Oceanic Niño Index (ONI) | NOAA Climate Prediction Center | Labelling each winter as El Niño, neutral, or La Niña |

**Downloading efficiently:** ECCC's daily data is served in files of one station and one year at a time (check the bulk data page for the current format). For 4 stations and 45 years that is about 180 files, so write a short Python loop with the `requests` library instead of downloading by hand. This is one of the most important time savers in a 4-week plan.

**How the ONI table is laid out:** it is a grid with one row per year and one column per 3-month season (DJF, JFM, and so on). The DJF value in the row for year *Y* covers December of *Y-1* to February of *Y*, so it matches `winter_year = Y` directly.

## 7. Tech Stack

| Layer | Tool | Purpose | Why it suits a beginner |
|---|---|---|---|
| Language | Python 3.11 or newer | Loading, cleaning, analysis | Most learning resources available |
| Data handling | pandas, NumPy | Clean and summarize tables, resampling | Core analyst skill |
| Data download | requests | Automate the station file downloads | Simple and widely used |
| Charts | matplotlib, seaborn | Box plots, timelines, comparisons | Simple to start, easy to polish |
| Database | SQLite | Store cleaned data, run SQL summaries | Built into Python, no server |
| Notebook | Jupyter Notebook or Google Colab | Step-by-step code and results | Good for learning and showing work |
| Dashboard | Tableau Public (Mac and Windows) or Power BI (Windows) | Interactive final visuals | Drag and drop, no coding |
| Version control | Git and GitHub | Save versions, publish the project | Undo mistakes, share your work |
| Editor | VS Code | Write scripts | Free and widely used |

**Install**
```
pip install pandas numpy matplotlib seaborn requests jupyter
```

**Time saver:** if installing Python locally takes more than an hour, use Google Colab and move to a local setup later.

**Dashboard note:** Tableau Public works best with CSV or Excel files, so export your tables from SQLite to CSV first.

## 8. Project Structure

```
ontario-elnino/
  config/
    stations.csv
  data/
    raw/
    processed/
  sql/
    winter_summary.sql
  notebooks/
    01_toronto_first_results.ipynb
    02_four_stations_and_sql.ipynb
    03_charts_and_findings.ipynb
  src/
    load.py
    clean.py
    summarize.py
  dashboard/
  reports/
  README.md
  requirements.txt
```

**stations.csv** is the only place station names appear, so adding a station later means adding one row:
```
station_id,name,region,latitude,longitude
<ECCC ID>,Windsor A,Southwest,...
<ECCC ID>,Toronto Pearson Intl A,Central,...
<ECCC ID>,Ottawa Macdonald-Cartier Intl A,East,...
<ECCC ID>,Thunder Bay A,Northwest,...
```

**Three reusable functions**
- `load_station(station_id)`: reads the raw files for a station
- `clean_station(df)`: fixes dates and units, flags impossible values, applies the data quality rule
- `winter_summary(df)`: calculates the measures in section 5

## 9. Database

| Table | Columns |
|---|---|
| `stations` | station_id, name, region, latitude, longitude |
| `daily_obs` | station_id, date, tmax, tmin, tmean, snowfall_cm |
| `enso_monthly` | year, month, oni |
| `winter_summary` | station_id, winter_year, mean_temp, temp_anomaly, snowfall_total_cm, snow_days, days_below_m20, enso_class |

**Example query (SQLite syntax, dates stored as text like `2024-01-15`)**
```sql
SELECT station_id,
       CASE WHEN CAST(strftime('%m', date) AS INTEGER) = 12
            THEN CAST(strftime('%Y', date) AS INTEGER) + 1
            ELSE CAST(strftime('%Y', date) AS INTEGER) END AS winter_year,
       AVG(tmean)                                        AS mean_temp,
       SUM(snowfall_cm)                                  AS snowfall_total_cm,
       SUM(CASE WHEN tmin <= -20 THEN 1 ELSE 0 END)      AS days_below_m20
FROM daily_obs
WHERE strftime('%m', date) IN ('12', '01', '02')
GROUP BY station_id, winter_year;
```

## 10. Analysis Plan

**Compare winter types.** For each station, calculate the average of every measure in El Niño, neutral, and La Niña winters, and the difference between El Niño and neutral. Show strong El Niño winters separately, remembering there are only about five.

**Charts**
1. Box plot of winter temperature anomaly by ENSO class, one panel per station
2. Bar chart of the El Niño minus neutral temperature difference by station, with confidence intervals (shows the south-to-north pattern)
3. Timeline of winter temperature anomaly, 1982 to 2026, El Niño winters highlighted, with a trend line
4. Box plot of total snowfall by ENSO class
5. Bar chart of very cold days by ENSO class

**Uncertainty.** With few winters in each group, show how uncertain every difference is. Calculate a **bootstrap 95% confidence interval** for each El Niño minus neutral difference by resampling the winters with replacement 10,000 times. If an interval includes zero, describe the result as inconclusive.

## 11. Dashboard Plan

Keep it simple. Three views built from exported CSV files:

1. **Map view:** the four stations with an ENSO class filter and a card showing average temperature anomaly
2. **Comparison view:** El Niño minus neutral difference by station and measure
3. **Timeline view:** winter anomalies by year, coloured by ENSO class, with a station selector

## 12. Using the Results (Recommendations)

The 2026-27 El Niño is expected to be strong, so the historical patterns can give context. This is not a forecast, and the advice should be framed as things to consider, with the uncertainty shown.

| If the historical results show... | A possible planning suggestion |
|---|---|
| Fewer snow days in El Niño winters | Municipal maintenance and winter tourism may consider a lower snow and salt budget, with a reserve for a big storm |
| Little or no difference | Plan as usual |
| Very cold days still occurring in El Niño winters | Keep cold-snap preparations in place |

Natural gas heating is not captured in this project's data, so avoid claims about total energy use.

## 13. Value and Limits

**Where it is useful:** it practises real data cleaning, SQL, statistics with small samples, and clear, honest reporting. A station-by-station Ontario comparison is easy to understand and timely given the 2026-27 El Niño.

**Where it is limited:** Environment Canada and NOAA already study El Niño's effects on Canada using far more data and better models. There are only about five strong El Niño winters and Ontario's signal is weak, so differences may be small or unclear. Present it as a transparent, reproducible station-level analysis, and state the limits plainly.

## 14. Risks and Limitations

| Risk | Effect | What to do |
|---|---|---|
| Only about five strong El Niño winters | Uncertain results | Show ranges, avoid strong claims, use bootstrap intervals |
| Missing data or station moves | Biased averages | 85 of 90 day rule, gap log, backup station rule |
| Warming trend | May look like an El Niño effect | Use anomalies and a trend line |
| Weak El Niño signal in Ontario | Small or no difference | Report it plainly; a null result is a valid finding |
| Many stations and measures | Some differences appear by chance | Focus on patterns that are consistent across stations |
| Reading association as cause | Overclaiming | State clearly that the analysis is not causal |
| **Tight 4-week schedule** | Rushing, errors | Use the buffer days, follow the cut list in Part B |

## 15. Definition of Done

- At least three stations (ideally four) are cleaned and summarized.
- The winter summary table exists both in pandas and in SQL.
- At least three of the five charts are finished.
- Every reported difference includes a bootstrap confidence interval.
- The report states what was found, how certain it is, and what the data cannot show.
- The GitHub repository has a README that lets someone else rerun your work.

---

# PART B: 4-WEEK ROADMAP

## Milestone Overview

| Week | Dates (2026) | Focus | Checkpoint |
|---|---|---|---|
| 1 | Sep 21-27 | Setup, Toronto data, first results | **Mini-project complete** |
| 2 | Sep 28-Oct 4 | Four stations and SQL | Combined table; SQL matches pandas |
| 3 | Oct 5-11 | Charts, uncertainty, findings | Five charts, confidence intervals, `findings.md` |
| 4 | Oct 12-18 | Dashboard, report, polish | Definition of done met |

Each week has 6 working days of about 2 hours, plus Day 7 as a buffer for catching up. **Do not skip the buffer days.** On a tight schedule they are what keeps small delays from becoming missed weeks.

**Honest note:** this is a tight schedule for a beginner. If you can only manage 6 to 8 hours a week, use the same plan over 6 weeks instead.

---

## Week 1: Setup, Toronto Data, First Results (Sep 21-27)

**Goal:** a complete mini-project for one station.

**Day 1: Setup (about 2 hours)**
1. Install Python 3.11 or newer and VS Code, or open Google Colab.
2. Run the `pip install` line and check that `import pandas` works.
3. Create a GitHub repository named `ontario-elnino` and the folder structure.
4. Write a short README (the question, four stations, data sources) and make your first commit.
5. Skim the official pandas "10 minutes to pandas" guide.

**Day 2: Get the Toronto data**
1. Find Toronto Pearson Intl A in the ECCC database and note its station ID and available years.
2. Write a short loop with `requests` to download each year's daily file into `data/raw/`. Never edit these files.
3. Combine the files into one table with `pd.concat`.

**Day 3: Clean the data and get ONI**
1. Inspect with `df.info()`, `df.describe()`, and `df.isna().sum()`.
2. Rename columns to `date`, `tmax`, `tmin`, `tmean`, `snowfall_cm`, `precip_mm`, and convert `date` with `pd.to_datetime`.
3. Count missing values per year and flag impossible values (`tmin` above `tmax`, temperatures below -50°C or above 45°C).
4. Download the ONI table, reshape it from wide to long with `melt`, and keep the DJF value per `winter_year`.

**Day 4: Winter measures**
1. Filter to December, January, and February and create `winter_year` (December belongs to the next year's winter).
2. Apply the 85 of 90 day rule.
3. Calculate mean temperature, total snowfall, snow days, and days with `tmin` at or below -20°C per winter.

**Day 5: Anomalies and ENSO groups**
1. Calculate the 1991-2020 average winter temperature and each winter's anomaly.
2. Merge with ONI, label each winter El Niño, neutral, or La Niña, and mark strong El Niño winters.
3. Use `groupby` to average each measure by ENSO class.

**Day 6: First charts**
1. Make the box plot of temperature anomaly by ENSO class and the timeline chart.
2. Write 3 to 4 sentences in the README describing what you see, and commit.

**Day 7: Buffer**

**Learn this week:** Git basics, `read_csv`, `concat`, `to_datetime`, `isna`, `melt`, `groupby`, `merge`, seaborn box plots

**Checkpoint:** the mini-project is complete. You have an answer for one station.

**Common problems:** ECCC column names include units and special characters (rename them), missing values may appear as blanks or text like "M", and `winter_year` can be off by one (test with December 1997 and January 1998, which should both give 1998).

---

## Week 2: Four Stations and SQL (Sep 28-Oct 4)

**Goal:** the same analysis for all four stations, plus a working SQL database.

**Day 1: Turn your code into functions**
1. Create `config/stations.csv` with all four stations.
2. Move your Week 1 code into `load_station`, `clean_station`, and `winter_summary` in the `src/` folder.
3. Test on Toronto and confirm the results match Week 1 exactly.

**Day 2: Run all four stations**
1. Download data for Windsor, Ottawa, and Thunder Bay using the same download loop.
2. Loop the three functions over all four stations and combine the outputs.

**Day 3: Check data quality**
1. Write the gap log: every dropped station-winter and the reason.
2. **Decision point:** if a station is too incomplete, apply the backup rule now (swap Ottawa for Sudbury, or go to three stations).
3. Save one combined `winter_summary.csv` (up to about 180 rows).

**Day 4: Build the database**
1. Create a SQLite database with Python's built-in `sqlite3` module.
2. Load `daily_obs` and `enso_monthly` using `df.to_sql`, with dates stored as `YYYY-MM-DD` text.

**Day 5: Reproduce the summary in SQL**
1. Run the example query in section 9 and save it in `sql/winter_summary.sql`.
2. Read the result into pandas with `pd.read_sql` and compare row counts and averages with your pandas table.

**Day 6: Extend the SQL**
1. Join with ENSO classes to produce the `winter_summary` table.
2. Write 3 more queries, such as average anomaly by ENSO class and station.
3. Commit.

**Day 7: Buffer**

**Learn this week:** writing functions, `for` loops, `pd.concat`, `SELECT`, `WHERE`, `GROUP BY`, `CASE`, `JOIN`, `strftime`

**Checkpoint:** one combined winter summary table, a gap log, and SQL output that matches pandas.

**Common problems:** each station has different missing periods (that is what the log is for), and SQL and pandas averages can differ when they treat missing values differently or when dates are not stored as text.

---

## Week 3: Charts, Uncertainty, Findings (Oct 5-11)

**Goal:** clear visuals, honest uncertainty, and written findings.

**Day 1: First two charts**
1. Box plot of temperature anomaly by ENSO class, one panel per station.
2. Box plot of total snowfall by ENSO class.

**Day 2: Remaining charts**
1. Bar chart of very cold days by ENSO class.
2. Timeline of anomalies with El Niño winters highlighted and a trend line.
3. Label every chart: title, units, and the number of winters in each group.

**Day 3: Differences table**
1. Build a table of El Niño minus neutral differences per station and measure.
2. Repeat it for strong El Niño winters only, and note how few winters that is.

**Day 4: Bootstrap intervals**
1. Resample the winters with replacement 10,000 times with `np.random.choice` and calculate a 95% confidence interval for each difference.
2. Save the intervals in the differences table.

**Day 5: Add intervals to the charts**
1. Build the bar chart of El Niño minus neutral temperature difference by station, with the intervals as error bars.
2. Check whether the south-to-north pattern is consistent.

**Day 6: Write findings**
1. In `findings.md`, write 5 to 8 findings, each with a caveat. For example: "Thunder Bay El Niño winters averaged X°C warmer than neutral winters, but the range is wide and only N winters were included."
2. Label any result whose interval includes zero as inconclusive.
3. Commit.

**Day 7: Buffer**

**Learn this week:** seaborn `FacetGrid`, bar charts with error bars, bootstrapping, describing uncertainty in plain language

**Checkpoint:** five charts, a differences table with confidence intervals, and a findings list.

**Common problems:** unreadable charts with too many panels (one metric per figure), forgetting to show group sizes, and over-interpreting small differences. Focus on patterns that repeat across stations.

---

## Week 4: Dashboard, Report, Polish (Oct 12-18)

**Goal:** a finished, presentable project.

**Day 1: Dashboard, first view**
1. Export `winter_summary` and the differences table to CSV.
2. Build the map view in Tableau Public or Power BI.

**Day 2: Dashboard, remaining views**
1. Build the comparison view and the timeline view.
2. Keep it simple: clear titles, one filter each.

**Day 3: Report, first half**
Write the first sections (about 4 to 6 pages in total):
1. Question and background
2. Data and stations
3. Methods
4. Results with charts

**Day 4: Report, second half**
5. Uncertainty and trend check
6. Recommendations and limitations
7. Conclusion

**Day 5: Repository**
1. Finish the README with steps to rerun the project.
2. Create `requirements.txt` with `pip freeze`.
3. Tidy the folders and remove unused files.

**Day 6: Final check**
1. Go through every item in the definition of done.
2. Re-read the report for statements that claim more than the data supports.
3. Commit the final version.

**Day 7: Buffer**

**Checkpoint:** the project meets the definition of done.

**Common problems:** spending too long polishing the dashboard. A simple, clear dashboard is enough.

---

## Weekly Habits

- Work in 2-hour sessions, six days a week.
- Commit at the end of every session.
- Keep a `notes.md` with problems you hit and how you fixed them. These become report material.
- When an error appears, read the last line first, then search or ask for help with the exact message.

## If You Fall Behind

Check progress at the end of each week. If you are more than a day behind, cut in this order:
1. **The dashboard:** replace it with the matplotlib charts (saves about 4 hours in Week 4)
2. **One station:** go to three stations, decided by the end of Week 2
3. **SQL depth:** keep only the single reproduced summary query and skip the extra queries

Do not cut: the winter summary, the ENSO comparison charts, the bootstrap intervals, and the limitations section. These are the core of the project.

## Left Out to Fit 4 Weeks (Optional Extensions)

- Permutation test as a second significance check
- Repeating the comparison after removing the linear warming trend
- Sudbury or London as a fifth station (just add a row to `stations.csv`)
- One BC or Alberta station, where the El Niño signal is expected to be stronger
- Electricity demand from IESO, Great Lakes ice cover, or the PDO index
- Comparing what actually happens in winter 2026-27 with the historical El Niño pattern once the season ends
