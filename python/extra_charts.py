"""Extra charts: latitude gradient, ENSO index vs anomaly, data-usability grid, ONI vs RONI.

Called from run_pipeline.py after create_charts(). Reads only the calculated tables,
so it never changes the analysis.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from matplotlib.lines import Line2D
import config as cfg
from viz_style import COLORS, apply_style, finish

INK = '#1f2937'
MUTED = '#64748b'
USABLE = '#2f6f73'      # teal: a usable winter
MISSING = '#e5e7eb'     # light grey: excluded winter
RNG = np.random.default_rng(cfg.RANDOM_SEED)


def _pair(comparison, index, metric, group='El Nino'):
    """El Nino (or Strong El Nino) minus Neutral rows for one index and metric."""
    return comparison.loc[comparison['enso_index'].eq(index) & comparison['metric'].eq(metric)
                          & comparison['comparison_group'].eq(group)
                          & comparison['reference_group'].eq('Neutral')].set_index('city')


def latitude_gradient(comparison, folder):
    """Difference (El Nino minus Neutral) against station latitude: the south-to-north question."""
    panels = [('mean_temp', 'Mean winter temperature', 'Difference (degrees C)'),
              ('snowfall_total_cm', 'Total winter snowfall', 'Difference (cm)'),
              ('snow_days', 'Snow days', 'Difference (days)')]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, (metric, title, ylabel) in zip(axes, panels):
        rows = _pair(comparison, cfg.PRIMARY_INDEX, metric)
        for k, (city, row) in enumerate(rows.sort_index(key=lambda i: [cfg.LATITUDES[c] for c in i]).iterrows()):
            if not np.isfinite(row['difference']):
                continue
            lat = cfg.LATITUDES[city]
            ax.plot([lat, lat], [row['ci_lower'], row['ci_upper']], color=COLORS['El Nino'], linewidth=1.8)
            ax.scatter(lat, row['difference'], s=40, color=COLORS['El Nino'], zorder=3)
            ax.annotate(f"{cfg.CITY_NAMES[city]}\nn={int(row['n_comparison'])}/{int(row['n_reference'])}",
                        (lat, row['ci_upper']), textcoords='offset points', xytext=(0, 5 + 22 * (k % 2)),
                        ha='center', fontsize=8, color=INK)
        ax.axhline(0, color=MUTED, linewidth=1)
        ax.margins(y=.18)
        ax.set(title=title, xlabel='Station latitude (degrees N)', ylabel=ylabel)
    fig.suptitle(f'El Nino minus Neutral by latitude | {cfg.PRIMARY_INDEX} | 95% intervals, n=El Nino/neutral winters')
    fig.text(.01, .005, 'Winters failing the missing-data rule are excluded, so group sizes differ by station. '
             'Snowfall covers different years at each station.', fontsize=8, color=MUTED)
    finish(fig, folder / 'latitude_gradient.png')


def _slope_ci(x, y, n=5000):
    """Bootstrap 95% interval for the least-squares slope, resampling winters."""
    slopes = []
    for _ in range(n):
        i = RNG.integers(0, len(x), len(x))
        if np.ptp(x[i]) > 0:
            slopes.append(np.polyfit(x[i], y[i], 1)[0])
    return np.percentile(slopes, [2.5, 97.5])


def index_vs_anomaly(winters, folder):
    """Winter temperature anomaly against the continuous DJF index value (all winters, no classes)."""
    index = cfg.PRIMARY_INDEX.lower()
    cities = sorted(winters['city'].unique(), key=lambda c: cfg.LATITUDES[c])
    fig, axes = plt.subplots(3, 2, figsize=(12, 11), sharex=True, sharey=True)
    for ax, city in zip(axes.flat, cities):
        block = winters.loc[winters['city'].eq(city)].dropna(subset=['temp_anomaly', 'enso_value'])
        for group in cfg.CLASS_ORDER:
            g = block.loc[block[f'enso_class_{index}'].eq(group)]
            ax.scatter(g['enso_value'], g['temp_anomaly'], s=22, color=COLORS[group], alpha=.85,
                       label=group, edgecolor='white', linewidth=.5)
        x, y = block['enso_value'].to_numpy(), block['temp_anomaly'].to_numpy()
        slope, intercept = np.polyfit(x, y, 1)
        lo, hi = _slope_ci(x, y)
        xs = np.array([x.min(), x.max()])
        ax.plot(xs, intercept + slope * xs, color=INK, linewidth=1.3)
        for v in (cfg.LA_NINA_THRESHOLD, cfg.EL_NINO_THRESHOLD):
            ax.axvline(v, color='#cbd5e1', linewidth=.8, linestyle=':')
        ax.axhline(0, color='#cbd5e1', linewidth=.8)
        r = np.corrcoef(x, y)[0, 1]
        ax.set_title(f'{cfg.CITY_NAMES[city]}: slope {slope:+.2f} °C per index unit '
                     f'({lo:+.2f} to {hi:+.2f}), r={r:.2f}, n={len(x)}', fontsize=9.5)
        ax.set(xlabel=f'DJF {cfg.PRIMARY_INDEX}', ylabel='Anomaly (degrees C)')
    handles = [Line2D([], [], marker='o', linestyle='', color=COLORS[g], label=g) for g in cfg.CLASS_ORDER]
    handles.append(Line2D([], [], color=INK, label='Least-squares fit'))
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(.5, .958), ncol=4, frameon=False)
    fig.suptitle(f'Winter temperature anomaly vs DJF {cfg.PRIMARY_INDEX} | all eligible winters')
    fig.text(.01, .005, 'Dotted lines mark the El Nino and La Nina thresholds. Slope intervals are bootstrap 95% '
             'intervals over winters.', fontsize=8, color=MUTED)
    finish(fig, folder / 'index_vs_temp_anomaly.png')


def usability_grid(winters, folder):
    """Which winters are usable for temperature and snowfall at each station, with the ENSO class on top."""
    index = cfg.PRIMARY_INDEX.lower()
    cities = sorted(winters['city'].unique(), key=lambda c: cfg.LATITUDES[c])
    years = list(range(cfg.FIRST_WINTER, cfg.LAST_WINTER + 1))
    fig, ax = plt.subplots(figsize=(13, 6.5))
    # ENSO strip (same for every station)
    enso = winters.drop_duplicates('winter_year').set_index('winter_year')[f'enso_class_{index}']
    for j, yr in enumerate(years):
        ax.add_patch(Rectangle((j, 0), .92, .7, color=COLORS.get(enso.get(yr), MISSING), linewidth=0))
    ax.text(-.5, .35, f'ENSO class ({cfg.PRIMARY_INDEX})', ha='right', va='center', fontsize=9, color=INK)
    y = 1.4
    for city in cities:
        block = winters.loc[winters['city'].eq(city)].set_index('winter_year')
        for label, flag in [('Temperature', 'temperature_pass'), ('Snowfall', 'snowfall_pass')]:
            for j, yr in enumerate(years):
                ok = bool(block[flag].get(yr, False))
                ax.add_patch(Rectangle((j, y), .92, .7, facecolor=USABLE if ok else MISSING, linewidth=0,
                                       hatch=None if ok else '////', edgecolor='white'))
            ax.text(-.5, y + .35, f'{cfg.CITY_NAMES[city]} {label.lower()}', ha='right', va='center',
                    fontsize=8.5, color=INK)
            n_ok = int(block[flag].sum())
            ax.text(len(years) + .1, y + .35, f'{n_ok}/{len(years)}', ha='left', va='center', fontsize=8.5, color=MUTED)
            y += .85
        y += .35
    ax.set_xlim(-.2, len(years) + 1.5)
    ax.set_ylim(y, -.3)
    ax.set_yticks([])
    ax.set_xticks([j + .46 for j in range(0, len(years), 5)], [years[j] for j in range(0, len(years), 5)])
    for s in ('left', 'bottom', 'top', 'right'):
        ax.spines[s].set_visible(False)
    ax.set_xlabel('Winter ending year')
    legend = [Patch(facecolor=USABLE, label='Usable winter'),
              Patch(facecolor=MISSING, hatch='////', edgecolor='white', label='Excluded (fails 3-and-5 rule or no data)')]
    legend += [Patch(facecolor=COLORS[g], label=g) for g in cfg.CLASS_ORDER]
    fig.legend(handles=legend, loc='upper center', bbox_to_anchor=(.55, .955), ncol=5, frameon=False, fontsize=8.5)
    fig.suptitle('Which winters can be used, by station and measure')
    fig.subplots_adjust(left=.22)
    fig.savefig(folder / 'winter_usability_grid.png', bbox_inches='tight')
    plt.close(fig)


def oni_vs_roni(comparison, folder):
    """Robustness check: the same El Nino minus Neutral difference under both indices."""
    panels = [('mean_temp', 'Mean winter temperature (degrees C)'),
              ('snowfall_total_cm', 'Total winter snowfall (cm)'),
              ('snow_days', 'Snow days (days)')]
    cities = sorted(comparison['city'].unique(), key=lambda c: cfg.LATITUDES[c])
    style = {'ONI': dict(color='#0f766e', marker='o', mfc='white'),
             'RONI': dict(color=INK, marker='o', mfc=INK)}
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5), sharey=True)
    for ax, (metric, title) in zip(axes, panels):
        for k, index in enumerate(['ONI', 'RONI']):
            rows = _pair(comparison, index, metric).reindex(cities)
            for pos, (city, row) in enumerate(rows.iterrows()):
                if not np.isfinite(row['difference']):
                    continue
                yy = pos + (-.15 if index == 'ONI' else .15)
                ax.plot([row['ci_lower'], row['ci_upper']], [yy, yy], color=style[index]['color'], linewidth=1.6)
                ax.plot(row['difference'], yy, marker='o', markersize=6, linestyle='',
                        color=style[index]['color'], markerfacecolor=style[index]['mfc'], zorder=3)
        ax.axvline(0, color=MUTED, linewidth=1)
        ax.set_yticks(range(len(cities)), [cfg.CITY_NAMES[c] for c in cities])
        ax.invert_yaxis()
        ax.set(title=title, xlabel='El Nino minus Neutral')
    handles = [Line2D([], [], marker='o', color=style[i]['color'], markerfacecolor=style[i]['mfc'], label=i)
               for i in ('ONI', 'RONI')]
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(.5, .958), ncol=2, frameon=False)
    fig.suptitle('Does the index choice change the answer? | 95% intervals')
    fig.text(.01, .005, 'Group sizes differ slightly between indices because the two indices label some winters differently.',
             fontsize=8, color=MUTED)
    finish(fig, folder / 'oni_vs_roni.png')


def create_extra_charts(winters, comparison, folder):
    folder.mkdir(parents=True, exist_ok=True)
    apply_style()
    latitude_gradient(comparison, folder)
    index_vs_anomaly(winters, folder)
    usability_grid(winters, folder)
    oni_vs_roni(comparison, folder)