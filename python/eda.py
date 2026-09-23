"""Create descriptive and ENSO comparison charts from the calculated tables."""
import numpy as np
import matplotlib.pyplot as plt
import config as cfg
from viz_style import COLORS, apply_style, finish


def snowfall_note(winters):
    """One-line footnote naming each station's last usable snowfall winter."""
    last = winters.loc[winters['snowfall_pass']].groupby('city')['winter_year'].max()
    ends = '; '.join(f"{cfg.CITY_NAMES[c]} {int(last[c])}" for c in sorted(last.index, key=lambda c: cfg.LATITUDES[c]))
    return ('Winters failing the missing-data rule are excluded. Last usable snowfall winter (ending year): '
            + ends + '.')


TEMP_NOTE = 'Winters failing the missing-data rule (3 consecutive / 5 total missing days per month) are excluded, so n differs by station.'


def create_charts(daily, winters, comparison, trends, folder):
    folder.mkdir(parents=True, exist_ok=True)
    apply_style()
    snow_note = snowfall_note(winters)
    index = cfg.PRIMARY_INDEX.lower()
    cities = sorted(winters['city'].unique(), key=lambda c: cfg.LATITUDES[c])
    # One panel per location. Always state sample counts and physical units.
    for metric, (label, unit) in cfg.METRICS.items():
        fig, axes = plt.subplots(3, 2, figsize=(12, 11), squeeze=False, sharey=True)
        for ax, city in zip(axes.flat, cities):
            block = winters.loc[winters['city'].eq(city)]
            values = [block.loc[block[f'enso_class_{index}'].eq(g), metric].dropna().to_numpy() for g in cfg.CLASS_ORDER]
            for pos, (group, values_group) in enumerate(zip(cfg.CLASS_ORDER, values), 1):
                if len(values_group):
                    bp = ax.boxplot([values_group], positions=[pos], widths=.55, patch_artist=True,
                                    medianprops={'color': 'black'}, showfliers=False)
                    bp['boxes'][0].set_facecolor(COLORS[group])
                    bp['boxes'][0].set_alpha(.65)
                    # Deterministic jitter keeps the same points visible in reruns.
                    offsets = np.linspace(-.12, .12, len(values_group))
                    ax.scatter(pos + offsets, values_group, s=12, color=COLORS[group], alpha=.65)
            ax.set_xticks([1, 2, 3], [f'{g}\nn={len(v)}' for g, v in zip(cfg.CLASS_ORDER, values)])
            ax.set(title=cfg.CITY_NAMES[city], ylabel=unit, xlim=(.5, 3.5))
            if metric == 'temp_anomaly':
                ax.axhline(0, color='#9ca3af', linewidth=.8)
        for ax in list(axes.flat)[len(cities):]:
            ax.set_visible(False)
        fig.suptitle(f'{label} by ENSO class | {cfg.PRIMARY_INDEX} | eligible winters ending {cfg.FIRST_WINTER}–{cfg.LAST_WINTER}')
        finish(fig, folder / f'{metric}_by_enso.png', snow_note if metric in ('snowfall_total_cm', 'snow_days') else TEMP_NOTE)

    for metric, (label, unit) in cfg.METRICS.items():
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=True)
        for ax, group in zip(axes, ['El Nino', 'Strong El Nino']):
            selected = comparison.loc[comparison['enso_index'].eq(cfg.PRIMARY_INDEX)
                & comparison['metric'].eq(metric) & comparison['comparison_group'].eq(group)
                & comparison['reference_group'].eq('Neutral')].set_index('city').reindex(cities)
            for pos, (_, row) in enumerate(selected.iterrows()):
                if np.isfinite(row['ci_lower']) and np.isfinite(row['ci_upper']):
                    ax.plot([row['ci_lower'], row['ci_upper']], [pos, pos], color=COLORS['El Nino'], linewidth=2)
                if np.isfinite(row['difference']):
                    ax.scatter(row['difference'], pos, color=COLORS['El Nino'], s=30)
            ax.axvline(0, color='#64748b', linewidth=1)
            labels = [f'{cfg.CITY_NAMES[c]} (n={int(selected.loc[c,"n_comparison"])}/{int(selected.loc[c,"n_reference"])})' for c in cities]
            ax.set_yticks(range(len(cities)), labels)
            ax.set(title=f'{group} minus Neutral', xlabel=f'Difference ({unit})')
            ax.invert_yaxis()
        fig.suptitle(f'{label} differences | {cfg.PRIMARY_INDEX} | percentile 95% intervals, n=comparison/reference')
        finish(fig, folder / f'{metric}_differences.png', snow_note if metric in ('snowfall_total_cm', 'snow_days') else TEMP_NOTE)

    fig, axes = plt.subplots(3, 2, figsize=(12, 10), sharey=True)
    for ax, city in zip(axes.flat, cities):
        block = winters.loc[winters['city'].eq(city)].sort_values('winter_year')
        ax.plot(block['winter_year'], block['temp_anomaly'], color='#b5bdc8', linewidth=1)
        for group in cfg.CLASS_ORDER:
            selected = block.loc[block[f'enso_class_{index}'].eq(group)]
            ax.scatter(selected['winter_year'], selected['temp_anomaly'], color=COLORS[group], s=20, label=group)
        trend = trends.set_index('city').loc[city]
        baseline = block['baseline_mean_temp'].iloc[0]
        if np.isfinite(trend['slope_c_per_decade']):
            fit = trend['intercept'] + trend['slope_c_per_decade']/10*block['winter_year'] - baseline
            ax.plot(block['winter_year'], fit, color='#252525', linestyle='--', linewidth=1, label='Linear trend')
        ax.axhline(0, color='#c7c7c7', linewidth=.7)
        gone = block.loc[block['temp_anomaly'].isna(), 'winter_year']
        if len(gone):  # tick marks along the bottom show excluded winters instead of hiding them
            ax.plot(gone, [.02] * len(gone), marker='|', linestyle='', color='#111827', markersize=9,
                    transform=ax.get_xaxis_transform(), label='Excluded winter (missing data)')
        ax.set(title=f"{cfg.CITY_NAMES[city]} ({int(block['temp_anomaly'].notna().sum())} of {len(block)} winters usable)",
               xlabel='Winter ending year', ylabel='Anomaly (degrees C)')
    for ax in list(axes.flat)[len(cities):]:
        ax.set_visible(False)
    seen = {}
    for ax in axes.flat:
        for h, l in zip(*ax.get_legend_handles_labels()):
            seen.setdefault(l, h)
    handles, labels = list(seen.values()), list(seen.keys())
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(.5, .958), ncol=5, frameon=False)
    fig.suptitle(f'Temperature anomalies | {cfg.PRIMARY_INDEX} | baseline: eligible winters ending {cfg.BASELINE_START}–{cfg.BASELINE_END}')
    finish(fig, folder / 'temperature_anomaly_timeline.png', TEMP_NOTE)

    fig, axes = plt.subplots(3, 2, figsize=(12, 10))
    for ax, city in zip(axes.flat, cities):
        block = winters.loc[winters['city'].eq(city)]
        for column, label in [('temperature_coverage_pct', 'Temperature'), ('snowfall_coverage_pct', 'Snowfall')]:
            ax.plot(block['winter_year'], block[column], label=label)
        ax.set(title=cfg.CITY_NAMES[city], xlabel='Winter ending year', ylabel='Valid daily measurements (%)', ylim=(-3, 103))
    for ax in list(axes.flat)[len(cities):]:
        ax.set_visible(False)
    axes.flat[0].legend(fontsize=8)
    fig.suptitle('Winter data coverage | absent dates count as missing measurements')
    finish(fig, folder / 'winter_data_coverage.png', 'Coverage counts absent dates as missing. Snowfall drops to zero where a station stopped reporting it.')