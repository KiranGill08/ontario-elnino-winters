# Ontario Winters and El Niño: Findings Report

**Study period:** winters 1981–82 to 2025–26 (45 winters) · **Stations:** Windsor, London, Toronto Pearson, Ottawa, Sudbury, Thunder Bay · **Primary ENSO index:** RONI · **Prepared:** September 2026

This is a historical analysis, not a forecast. It describes how El Niño winters in Ontario differed from other winters in the past. It shows associations, not proof that El Niño caused them.

## Summary

- **Strong El Niño winters were clearly warmer.** At five of six stations, Strong El Niño winters were 2.4–4.1 °C warmer than neutral winters, and the intervals exclude zero. For all El Niño winters together, every station was warmer (+0.8 to +2.3 °C), but no single station's interval clears zero.
- **The warming was largest in the north.** Thunder Bay showed the biggest difference (+4.1 °C in Strong El Niño winters) and the strongest link between El Niño strength and winter temperature. Its El Niño effect was significantly larger than Toronto's.
- **Southern Ontario had fewer snow days.** Toronto averaged 6 fewer snow days in El Niño winters and 9 fewer in Strong El Niño winters; Windsor 8 and 12 fewer. Both results clear zero. Farther north, snow results were inconclusive.
- **Very cold days (−20 °C or colder) were fewer**, most clearly in Strong El Niño winters at Thunder Bay (16 fewer), Windsor and Toronto.
- **Every one of the 48 El Niño comparisons points the same way:** warmer, less snow, fewer snow days and fewer very cold days. 18 of them clear zero, far more than the 2 or 3 expected by chance.
- **Beyond the weather**, Thunder Bay's heating demand was lower in El Niño winters (borderline), and more spring freeze-thaw days went with more maple syrup, although that link is not shown to be an El Niño effect.

## 1. Question and background

**Were El Niño winters in Ontario warmer, less snowy, or less extreme than other winters, and did the pattern differ from south to north?**

El Niño is a periodic warming of the tropical Pacific Ocean that shifts weather patterns across North America. Winter planners in Ontario, such as municipal snow-clearing crews, winter tourism operators and cold-weather response teams, often hear that an El Niño winter will be mild. This project checks what 45 years of station records actually show. The six business questions are:

| ID | Question |
|---|---|
| BQ1 | Were El Niño winters warmer than neutral winters at each location? |
| BQ2 | Did El Niño winters receive less snowfall? |
| BQ3 | Did El Niño winters have fewer very cold days? |
| BQ4 | Was the pattern different between southern and northern locations? |
| BQ5 | Did El Niño winters have fewer days with substantial new snowfall? |
| BQ6 | Were differences larger in strong El Niño winters? |

## 2. Data and stations

Daily temperature and snowfall came from Environment and Climate Change Canada's historical climate data for six stations, 98,096 daily records in total. ENSO values came from NOAA's Relative Oceanic Niño Index (RONI), with the older ONI used as a cross-check. The impact analyses also used Statistics Canada data on Ontario maple syrup production and Ontario real GDP.

| Station | Latitude | Usable winters, temperature | Usable winters, snowfall |
|---|---:|---:|---:|
| Windsor | 42.3° N | 39 of 45 | 31 of 45 |
| London | 43.0° N | 44 of 45 | 20 of 45 |
| Toronto Pearson | 43.7° N | 45 of 45 | 37 of 45 |
| Ottawa | 45.3° N | 43 of 45 | 40 of 45 |
| Sudbury | 46.6° N | 40 of 45 | 36 of 45 |
| Thunder Bay | 48.4° N | 42 of 45 | 12 of 45 |

Temperature records are nearly complete. Snowfall records are not: London and Thunder Bay stopped reporting snowfall around 2003, so their snow results rest on few winters. The chart below shows which winters could be used for each station and measure.

![Which winters can be used, by station and measure](figures/winter_usability_grid.png)

Of the 45 winters, RONI classifies 16 as El Niño, 9 as neutral and 20 as La Niña. Five El Niño winters were strong (RONI of +1.5 or more): 1982–83, 1986–87, 1991–92, 1997–98 and 2015–16.

## 3. Methods

- **Winter:** December to February, named by the year February falls in.
- **Measures per station and winter:** mean temperature and its anomaly (difference from the station's 1991–2020 winter average), total snowfall, snow days (at least 1 cm of new snow), and very cold days (minimum temperature at or below −20 °C).
- **Data quality:** a winter is used for a measure only if every month passes the WMO "3 and 5" rule: no more than 3 consecutive and 5 total missing days. Missing values are never filled in.
- **ENSO classes** from the DJF RONI value: El Niño at +0.5 or higher (Strong at +1.5 or higher), La Niña at −0.5 or lower, and neutral in between.
- **Comparison:** at each station, the average of El Niño winters minus the average of neutral winters.
- **Uncertainty:** every difference has a bootstrap 95% confidence interval from 10,000 resamples of whole winters. A result is called significant only when its interval excludes zero. Otherwise it is inconclusive: the data cannot rule out no difference.
- **Checks:** results were repeated after removing each station's long-term warming trend, and again with ONI instead of RONI.

## 4. Results

### 4.1 Temperature (BQ1, BQ6)

| Station | El Niño − neutral (°C) | Strong El Niño − neutral (°C) |
|---|---|---|
| Windsor | +1.3 [−0.4, +3.0] | **+2.6 [+0.8, +4.3]** |
| London | +1.4 [−0.5, +3.2] | **+2.6 [+0.7, +4.4]** |
| Toronto Pearson | +1.3 [−0.5, +3.0] | **+2.4 [+0.4, +4.2]** |
| Ottawa | +0.8 [−1.1, +2.4] | +1.4 [−0.7, +3.4] |
| Sudbury | +1.8 [−0.2, +3.5] | **+3.1 [+1.1, +4.9]** |
| Thunder Bay | +2.3 [−0.0, +4.6] | **+4.1 [+1.9, +6.2]** |

*Brackets show the 95% interval. Bold results exclude zero.*

El Niño winters were warmer at every station, but with only 9 neutral winters for comparison, no single station's interval for all El Niño winters excludes zero. Thunder Bay comes closest. Strong El Niño winters show a much clearer signal: roughly twice the warming, significant at five of six stations. Ottawa is the exception, with the smallest differences throughout.

![Temperature anomaly differences](figures/temp_anomaly_differences.png)

The strength of El Niño matters, not just its presence. Across all winters, a stronger El Niño went with a warmer winter at every station, most clearly at Thunder Bay: about +0.9 °C per unit of RONI (95% interval +0.3 to +1.4; r = 0.40). At the other stations the slopes were +0.2 to +0.4 °C per unit, with intervals that include zero.

![ENSO strength vs. temperature anomaly](figures/index_vs_temp_anomaly.png)

### 4.2 Snow (BQ2, BQ5)

| Station | Snow days: El Niño − neutral | Snow days: Strong − neutral | Snowfall (cm): Strong − neutral |
|---|---|---|---|
| Windsor | **−7.5 [−13.7, −1.7]** | **−12.4 [−19.5, −5.6]** | **−61 [−105, −21]** |
| London | −6.8 [−14.1, +1.5] | **−11.8 [−18.0, −5.2]** | **−52 [−101, −0.4]** |
| Toronto Pearson | **−6.1 [−9.6, −2.5]** | **−9.4 [−12.5, −6.0]** | **−30 [−52, −8]** |
| Ottawa | −2.1 [−7.2, +2.5] | −4.1 [−9.7, +1.1] | −11 [−49, +28] |
| Sudbury | −1.9 [−7.0, +3.0] | −2.2 [−7.5, +2.8] | −28 [−79, +28] |
| Thunder Bay | −5.5 [−13.7, +2.3] | −3.0 [−10.3, +4.3] | −18 [−44, +4] |

El Niño winters had fewer snow days and less snow everywhere, but the clear results are in the south. Toronto and Windsor had significantly fewer snow days in both El Niño and Strong El Niño winters, and Strong El Niño winters brought 30–60 cm less snow in Windsor, London and Toronto. In Ottawa and Sudbury the differences were smaller and inconclusive.

Thunder Bay's snow results rest on very few winters (6 El Niño and 3 neutral), so they should not be relied on. Its one significant result, 32 cm less snowfall in El Niño winters, appears in the snowfall chart below but is not treated as a finding.

![Snow day differences](figures/snow_days_differences.png)

![Total snowfall differences](figures/snowfall_total_cm_differences.png)

### 4.3 Very cold days (BQ3)

Very cold days were fewer in El Niño winters at every station. The clearest results were in Strong El Niño winters: Thunder Bay had 16 fewer days at or below −20 °C (95% interval −28 to −4.5), Toronto 3.4 fewer and Windsor 2.4 fewer. Windsor was also significant for all El Niño winters (2.0 fewer). Elsewhere the differences were inconclusive, and severe cold still occurred in El Niño winters at every northern station.

![Very cold day differences](figures/days_below_m20_differences.png)

### 4.4 South vs. north (BQ4)

![El Niño minus neutral by latitude](figures/latitude_gradient.png)

The temperature effect grows toward the north, while the clear snow effects are in the south. Thunder Bay's El Niño warming was 1.2 °C larger than Toronto's (95% interval +0.2 to +2.3), a significant difference. Compared with Windsor, the difference was 1.0 °C (−0.1 to +2.1), just short of significant. North–south differences in snow and cold days were inconclusive, largely because of the snowfall gaps at the northern stations.

### 4.5 Beyond the weather

- **Heating demand:** heating-degree-days (base 18 °C) were 3–7% lower in El Niño winters at all six stations. Only Thunder Bay's result (−7.4%, 95% interval −15.0% to −0.0%) excludes zero, and only just, so it should be treated as borderline.
- **Maple syrup:** years with more freeze-thaw days in the February–April sap season produced more maple syrup than the long-term trend (r = +0.28, 95% interval +0.06 to +0.49). However, El Niño did not significantly change the number of freeze-thaw days (−2.3 days, interval −6.1 to +1.3). The maple link is real, but it is not shown to be an El Niño effect.
- **Growing season:** the frost-free season was 5–11 days longer after El Niño winters at every station, but every interval includes zero, including the province-wide average (+5.4 days, −2.6 to +13.8).
- **Economy:** Ontario's real GDP growth showed no relationship with El Niño (+0.9 percentage points, −1.5 to +3.4). Its large swings are all recessions. A real winter-weather effect is too small to show up in the provincial economy.

![Heating demand by city](figures/eda_heating_demand_by_city.png)

![Freeze-thaw days vs. maple production](figures/eda_freeze_thaw_vs_maple.png)

## 5. Uncertainty and robustness

**Long-term warming.** Winters warmed at every station over the study period, by 0.15 to 0.48 °C per decade. Toronto warmed fastest. Removing each station's trend barely changed the results: Strong El Niño winters remained significantly warmer at the same five stations (+2.5 to +4.2 °C). The El Niño signal is not a side effect of recent warm winters.

![Temperature anomaly timeline with trend](figures/temperature_anomaly_timeline.png)

**Index choice.** Repeating every comparison with ONI instead of RONI gave the same verdict (significant or inconclusive) in 89% of cases. The conclusions do not depend on the index.

**Small groups.** Only 9 winters were neutral, and only 5 were strong El Niño winters. Each result depends on a handful of winters, so one unusual winter can move an average noticeably. This is why most intervals are wide.

**Many comparisons.** This report makes 48 El Niño and Strong El Niño comparisons. At a 95% level, about 2 or 3 would clear zero by chance alone; 18 did, and all 48 point in the same direction. The overall pattern is well supported, but any single result, especially a borderline one, could be a chance finding.

## 6. Recommendations

For winter planners, as historical context rather than a forecast:

1. **Southern Ontario (Toronto, Windsor, London):** past El Niño winters, and strong ones especially, had noticeably fewer snow days. This is a reasonable basis for discussing winter budgets and staffing scenarios, but not for cutting capacity. Several El Niño winters were still snowy.
2. **Northern Ontario (Sudbury, Thunder Bay):** expect the largest temperature difference in strong El Niño winters, but keep planning for severe cold. Very cold days were fewer, not absent.
3. **Ottawa:** El Niño showed the weakest link to winter conditions here. Normal winter planning applies.
4. **Use the strength of the event.** Strong El Niño winters differed from neutral winters about twice as much as El Niño winters overall. If the next El Niño is forecast to be strong, the strong-event results are the relevant comparison.
5. **Improve the snow record.** Adding stations with complete snowfall records in northern Ontario would make the snow findings far more reliable.

## 7. Limitations

- **Association, not cause.** El Niño winters also differ in other ways, and other climate patterns affect Ontario winters.
- **Small samples.** 9 neutral and 5 strong El Niño winters limit precision. Results for individual stations should be read together, not in isolation.
- **Snowfall gaps.** London and Thunder Bay have no snowfall data after about 2003, and Windsor after 2014. Their snow results cover different years from the other stations.
- **Station changes.** Some locations combine records from more than one station ID over time.
- **Six stations** cannot represent all of Ontario, especially the far north.
- **Heating demand** is measured with heating-degree-days, not actual energy use or bills.

## 8. Conclusion

Over 45 winters, El Niño winters in Ontario were consistently milder than neutral winters: warmer, with fewer snow days, less snow and fewer severe cold days. The pattern is clearest in strong El Niño winters. The temperature effect was largest in the north, especially Thunder Bay, while the clearest snow effects were in the south, especially Toronto and Windsor. Individual results are uncertain because the number of winters is small, but the consistency of direction across every station and measure makes the overall pattern credible as historical context for winter planning.

## Appendix

**Reproducing these results.** Run `python python/run_pipeline.py` from the repository folder. Each run writes its charts to `runs/<timestamp>/figures/` and the data behind every chart to `runs/<timestamp>/data/chart_data/`. The report's charts are copies from that run, kept in `reports/figures/`.

**Other charts** produced by the pipeline and not shown here: the box plots of each measure by ENSO class (`*_by_enso.png`), ONI vs. RONI (`oni_vs_roni.png`), growing-season length (`eda_growing_season_by_city.png`) and GDP growth (`eda_gdp_growth_vs_enso.png`).

**Sources:** Environment and Climate Change Canada, Historical Climate Data (daily station records); NOAA Climate Prediction Center, RONI and ONI; Statistics Canada tables 32-10-0354-01 (maple products) and 36-10-0222-01 (GDP).
