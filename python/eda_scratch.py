"""Quick, exploratory charts for looking at the data as you work.

These are NOT part of the validated pipeline output (that's eda.py and
extra_charts.py, which run_pipeline.py calls automatically and which ship to
dashboard/figures/). This file is a scratch space for one-off EDA charts you
want to look at without rerunning the full pipeline. Each chart is saved into
reports/ instead.

Run directly, any time after run_pipeline.py has produced
data/processed/winter_kpis.csv:

    python python/eda_scratch.py

To add a new EDA chart later: write a new function that takes the winters
DataFrame and calls finish(fig, REPORTS / 'your_file.png'), then call it from
main().
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

import config as cfg
from viz_style import COLORS, apply_style, finish

REPORTS = cfg.ROOT / 'reports'


def load_winter_kpis():
    path = cfg.ROOT / 'data' / 'processed' / 'winter_kpis.csv'
    if not path.is_file():
        raise SystemExit(f'Missing {path} -- run python/run_pipeline.py first.')
    return pd.read_csv(path)


def load_enso_comparisons():
    path = cfg.ROOT / 'data' / 'processed' / 'enso_comparisons.csv'
    if not path.is_file():
        raise SystemExit(f'Missing {path} -- run python/run_pipeline.py first.')
    return pd.read_csv(path)


def load_temperature_trends():
    path = cfg.ROOT / 'data' / 'processed' / 'temperature_trends.csv'
    if not path.is_file():
        raise SystemExit(f'Missing {path} -- run python/run_pipeline.py first.')
    return pd.read_csv(path)


def boxplot_anomaly_by_enso(winters):
    """Box plot of winter temperature anomaly by ENSO class, one panel per station."""
    index = cfg.PRIMARY_INDEX.lower()
    eligible = winters.loc[winters['temperature_pass'] & winters['temp_anomaly'].notna()]
    cities = sorted(eligible['city'].unique(), key=lambda c: cfg.LATITUDES[c])

    fig, axes = plt.subplots(2, 3, figsize=(11.5, 7.2), sharey=True)
    for ax, city in zip(axes.flat, cities):
        block = eligible.loc[eligible['city'].eq(city)]
        values = [block.loc[block[f'enso_class_{index}'].eq(g), 'temp_anomaly'].to_numpy()
                  for g in cfg.CLASS_ORDER]
        bp = ax.boxplot(values, patch_artist=True, widths=0.55,
                         medianprops={'color': '#1e293b', 'linewidth': 1.6},
                         whiskerprops={'color': '#475569'}, capprops={'color': '#475569'},
                         flierprops={'marker': 'o', 'markersize': 3.5, 'markerfacecolor': 'none',
                                     'markeredgecolor': '#94a3b8'})
        for patch, group in zip(bp['boxes'], cfg.CLASS_ORDER):
            patch.set_facecolor(COLORS[group])
            patch.set_alpha(0.85)
            patch.set_edgecolor('#1e293b')
            patch.set_linewidth(0.8)
        ax.axhline(0, color='#94a3b8', linewidth=1, linestyle='--', zorder=0)
        ax.set_xticks(range(1, len(cfg.CLASS_ORDER) + 1),
                      [f'{g}\n(n={len(v)})' for g, v in zip(cfg.CLASS_ORDER, values)], fontsize=8.5)
        ax.set_title(cfg.CITY_NAMES[city], fontsize=11.5, fontweight='bold', pad=8)
        ax.tick_params(axis='y', labelsize=9)
    for ax in list(axes.flat)[len(cities):]:
        ax.set_visible(False)
    for ax in axes[:, 0]:
        ax.set_ylabel('Temp anomaly (°C)\nvs 1991-2020 baseline', fontsize=9)

    fig.suptitle('Winter temperature anomaly by ENSO class, by station', fontsize=15, y=0.985)
    note = (f'{cfg.PRIMARY_INDEX} classification. Eligible winters only (temperature_pass). '
            'Exploratory: see enso_comparisons.csv for the bootstrap significance test on the means.')
    finish(fig, REPORTS / 'eda_temp_anomaly_by_enso.png', note)
    print(f'Saved {REPORTS / "eda_temp_anomaly_by_enso.png"}')


def barchart_el_nino_minus_neutral(comparisons):
    """Bar chart of the El Nino minus Neutral mean-temperature difference by
    station, with 95% bootstrap confidence intervals. Stations are ordered
    south to north, so the bars show the latitude gradient directly."""
    selected = comparisons.loc[
        comparisons['enso_index'].eq(cfg.PRIMARY_INDEX)
        & comparisons['metric'].eq('mean_temp')
        & comparisons['comparison_group'].eq('El Nino')
        & comparisons['reference_group'].eq('Neutral')
    ].sort_values('latitude_approx')

    x = range(len(selected))
    diffs = selected['difference'].to_numpy()
    err_low = diffs - selected['ci_lower'].to_numpy()
    err_high = selected['ci_upper'].to_numpy() - diffs

    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.bar(x, diffs, width=0.6, color=COLORS['El Nino'], alpha=0.85,
                  edgecolor='#1e293b', linewidth=0.8, zorder=3)
    ax.errorbar(x, diffs, yerr=[err_low, err_high], fmt='none', ecolor='#1e293b',
                elinewidth=1.4, capsize=5, zorder=4)
    ax.axhline(0, color='#475569', linewidth=1)

    for xi, row in zip(x, selected.itertuples()):
        marker = '*' if row.status == 'interval_excludes_zero' else ''
        va = 'bottom' if row.difference >= 0 else 'top'
        offset = (row.ci_upper - row.difference if row.difference >= 0
                  else row.difference - row.ci_lower)
        y = row.difference + offset if row.difference >= 0 else row.difference - offset
        ax.annotate(f'{row.difference:+.2f}{marker}', (xi, y),
                    xytext=(0, 6 if row.difference >= 0 else -6), textcoords='offset points',
                    ha='center', va=va, fontsize=9.5, fontweight='bold', color='#1e293b')

    ax.set_xticks(list(x), [cfg.CITY_NAMES[c] for c in selected['city']], fontsize=9.5)
    ax.set_ylabel('Mean winter temperature, El Nino minus Neutral (°C)')
    ax.set_title('El Nino minus Neutral winter temperature, south to north', fontsize=14, pad=12)

    note = (f'{cfg.PRIMARY_INDEX} classification, mean_temp. Error bars are 95% bootstrap intervals '
            f'({cfg.BOOTSTRAP_SAMPLES:,} resamples). * = interval excludes zero. Stations ordered by '
            'latitude (Windsor south to Thunder Bay north).')
    finish(fig, REPORTS / 'eda_el_nino_minus_neutral_by_station.png', note)
    print(f'Saved {REPORTS / "eda_el_nino_minus_neutral_by_station.png"}')


def timeline_anomaly_with_trend(winters, trends):
    """Timeline of winter temperature anomaly, one panel per station, El Nino
    winters highlighted, with a per-city linear trend line overlaid."""
    index = cfg.PRIMARY_INDEX.lower()
    cities = sorted(winters['city'].unique(), key=lambda c: cfg.LATITUDES[c])

    fig, axes = plt.subplots(2, 3, figsize=(13, 8), sharey=True)
    for ax, city in zip(axes.flat, cities):
        block = winters.loc[winters['city'].eq(city)].sort_values('winter_year')
        ax.plot(block['winter_year'], block['temp_anomaly'], color='#b5bdc8', linewidth=1, zorder=1)
        for group in cfg.CLASS_ORDER:
            selected = block.loc[block[f'enso_class_{index}'].eq(group)]
            ax.scatter(selected['winter_year'], selected['temp_anomaly'], color=COLORS[group],
                       s=22, label=group, zorder=2, edgecolor='white', linewidth=0.4)
        trend = trends.set_index('city').loc[city]
        baseline = block['baseline_mean_temp'].iloc[0]
        if pd.notna(trend['slope_c_per_decade']):
            fit = trend['intercept'] + trend['slope_c_per_decade'] / 10 * block['winter_year'] - baseline
            ax.plot(block['winter_year'], fit, color='#1e293b', linestyle='--', linewidth=1.3,
                    label='Linear trend', zorder=3)
        ax.axhline(0, color='#c7c7c7', linewidth=0.7, zorder=0)
        gone = block.loc[block['temp_anomaly'].isna(), 'winter_year']
        if len(gone):
            ax.plot(gone, [0.02] * len(gone), marker='|', linestyle='', color='#111827', markersize=9,
                    transform=ax.get_xaxis_transform(), label='Excluded winter (missing data)')
        usable = int(block['temp_anomaly'].notna().sum())
        ax.set_title(f'{cfg.CITY_NAMES[city]} ({usable} of {len(block)} winters usable)',
                     fontsize=11, fontweight='bold', pad=8)
        ax.set_xlabel('Winter ending year', fontsize=9)
    for ax in axes[:, 0]:
        ax.set_ylabel('Anomaly (°C)', fontsize=9)

    seen = {}
    for ax in axes.flat:
        for h, l in zip(*ax.get_legend_handles_labels()):
            seen.setdefault(l, h)
    fig.legend(list(seen.values()), list(seen.keys()), loc='upper center',
               bbox_to_anchor=(0.5, 0.965), ncol=5, frameon=False, fontsize=9.5)
    fig.suptitle(f'Winter temperature anomaly, {cfg.FIRST_WINTER}–{cfg.LAST_WINTER}, El Nino winters highlighted',
                 fontsize=14.5, y=1.01)

    note = (f'{cfg.PRIMARY_INDEX} classification. Baseline: eligible winters ending {cfg.BASELINE_START}–{cfg.BASELINE_END}. '
            'Dashed line is each city’s own linear trend (temperature_trends.csv), not a fit to El Nino winters alone.')
    finish(fig, REPORTS / 'eda_temp_anomaly_timeline.png', note)
    print(f'Saved {REPORTS / "eda_temp_anomaly_timeline.png"}')


def boxplot_snowfall_by_enso(winters):
    """Box plot of total winter snowfall by ENSO class, one panel per station."""
    index = cfg.PRIMARY_INDEX.lower()
    eligible = winters.loc[winters['snowfall_pass'] & winters['snowfall_total_cm'].notna()]
    cities = sorted(eligible['city'].unique(), key=lambda c: cfg.LATITUDES[c])

    # Snowfall records end earlier than temperature records at several stations --
    # name each city's last usable snowfall winter so the sample-size gap is explicit.
    last_usable = eligible.groupby('city')['winter_year'].max()
    ends = '; '.join(f'{cfg.CITY_NAMES[c]} {int(last_usable[c])}' for c in cities)

    fig, axes = plt.subplots(2, 3, figsize=(11.5, 7.2), sharey=True)
    for ax, city in zip(axes.flat, cities):
        block = eligible.loc[eligible['city'].eq(city)]
        values = [block.loc[block[f'enso_class_{index}'].eq(g), 'snowfall_total_cm'].to_numpy()
                  for g in cfg.CLASS_ORDER]
        bp = ax.boxplot(values, patch_artist=True, widths=0.55,
                         medianprops={'color': '#1e293b', 'linewidth': 1.6},
                         whiskerprops={'color': '#475569'}, capprops={'color': '#475569'},
                         flierprops={'marker': 'o', 'markersize': 3.5, 'markerfacecolor': 'none',
                                     'markeredgecolor': '#94a3b8'})
        for patch, group in zip(bp['boxes'], cfg.CLASS_ORDER):
            patch.set_facecolor(COLORS[group])
            patch.set_alpha(0.85)
            patch.set_edgecolor('#1e293b')
            patch.set_linewidth(0.8)
        ax.set_xticks(range(1, len(cfg.CLASS_ORDER) + 1),
                      [f'{g}\n(n={len(v)})' for g, v in zip(cfg.CLASS_ORDER, values)], fontsize=8.5)
        ax.set_title(cfg.CITY_NAMES[city], fontsize=11.5, fontweight='bold', pad=8)
        ax.tick_params(axis='y', labelsize=9)
        ax.set_ylim(bottom=0)
    for ax in list(axes.flat)[len(cities):]:
        ax.set_visible(False)
    for ax in axes[:, 0]:
        ax.set_ylabel('Total winter snowfall (cm)', fontsize=9)

    fig.suptitle('Total winter snowfall by ENSO class, by station', fontsize=15, y=0.985)
    note = (f'{cfg.PRIMARY_INDEX} classification. Eligible winters only (snowfall_pass). Last usable snowfall winter '
            f'(ending year): {ends}. Sample sizes differ across cities for this reason, not just ENSO class. '
            'Exploratory: see enso_comparisons.csv for the bootstrap significance test on the means.')
    finish(fig, REPORTS / 'eda_snowfall_by_enso.png', note)
    print(f'Saved {REPORTS / "eda_snowfall_by_enso.png"}')


def barchart_cold_days_by_enso(winters):
    """Bar chart of mean very-cold days (below -20C) by ENSO class, one panel
    per station. Error bars are the standard error of the mean."""
    index = cfg.PRIMARY_INDEX.lower()
    eligible = winters.loc[winters['cold_days_pass'] & winters['days_below_m20'].notna()]
    cities = sorted(eligible['city'].unique(), key=lambda c: cfg.LATITUDES[c])

    fig, axes = plt.subplots(2, 3, figsize=(11.5, 7.2), sharey=True)
    for ax, city in zip(axes.flat, cities):
        block = eligible.loc[eligible['city'].eq(city)]
        groups = [block.loc[block[f'enso_class_{index}'].eq(g), 'days_below_m20'] for g in cfg.CLASS_ORDER]
        means = [g.mean() for g in groups]
        sems = [g.std(ddof=1) / len(g) ** 0.5 if len(g) > 1 else 0 for g in groups]
        x = range(len(cfg.CLASS_ORDER))
        colors = [COLORS[g] for g in cfg.CLASS_ORDER]
        ax.bar(x, means, yerr=sems, capsize=4, width=0.6, color=colors, alpha=0.85,
              edgecolor='#1e293b', linewidth=0.8, error_kw={'ecolor': '#1e293b', 'elinewidth': 1.2})
        ax.set_xticks(list(x), [f'{g}\n(n={len(v)})' for g, v in zip(cfg.CLASS_ORDER, groups)], fontsize=8.5)
        ax.set_title(cfg.CITY_NAMES[city], fontsize=11.5, fontweight='bold', pad=8)
        ax.tick_params(axis='y', labelsize=9)
    for ax in list(axes.flat)[len(cities):]:
        ax.set_visible(False)
    for ax in axes[:, 0]:
        ax.set_ylabel('Very cold days (below -20°C)', fontsize=9)

    fig.suptitle('Very cold days by ENSO class, by station', fontsize=15, y=0.985)
    note = (f'{cfg.PRIMARY_INDEX} classification. Eligible winters only (cold_days_pass). Bars are the group mean, '
            'error bars are +-1 standard error of the mean (not a bootstrap interval). Southern stations (Windsor, '
            'Toronto Pearson, London) have very few very-cold days overall, so their bars sit close to zero. '
            'Exploratory: see enso_comparisons.csv for the bootstrap significance test.')
    finish(fig, REPORTS / 'eda_cold_days_by_enso.png', note)
    print(f'Saved {REPORTS / "eda_cold_days_by_enso.png"}')


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    apply_style()
    winters = load_winter_kpis()
    boxplot_anomaly_by_enso(winters)
    comparisons = load_enso_comparisons()
    barchart_el_nino_minus_neutral(comparisons)
    trends = load_temperature_trends()
    timeline_anomaly_with_trend(winters, trends)
    boxplot_snowfall_by_enso(winters)
    barchart_cold_days_by_enso(winters)


if __name__ == '__main__':
    main()