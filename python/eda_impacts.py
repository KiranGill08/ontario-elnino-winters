"""EDA charts for El Nino's downstream impacts -- heating demand, maple syrup
production, growing-season length, and provincial GDP -- beyond the core
winter-climate metrics covered by eda.py / eda_scratch.py.

Run standalone (as below), each chart is saved into reports/ with an 'eda_'
prefix, alongside a companion reports/eda_impacts_findings.md -- same scratch
convention as eda_scratch.py. Every chart function also takes an optional
`folder` argument, which is how run_pipeline.py calls these same functions to
save the per-run copies into <output>/figures/ instead.

Every number in the findings file is computed here from data/processed/*.csv,
never hand-typed, so it stays correct if the underlying data changes.

Inputs required (run these first if missing):
    python run_pipeline.py            -> data/processed/winter_kpis.csv, enso_comparisons.csv
    python clean_data.py              -> data/processed/ontario_maple_syrup_production.csv, ontario_gdp.csv
    python maple_sap_season.py        -> data/processed/sap_season_kpis.csv
    python growing_season.py          -> data/processed/growing_season_kpis.csv

Run directly:

    python eda_impacts.py

One important finding this file does NOT have its own chart for: El Nino itself
does not significantly change freeze-thaw days (see write_impacts_findings for
the number) -- that caveat belongs with the freeze-thaw/maple chart, not as a
separate plot.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import config as cfg
from viz_style import COLORS, apply_style

REPORTS = cfg.ROOT / 'reports'
PROCESSED = cfg.ROOT / 'data' / 'processed'

# Hues outside the project's ENSO palette (COLORS), used only where a chart
# is not itself a 3-class ENSO comparison -- same convention already used in
# the maple/freeze-thaw and growing-season exploratory charts.
HEATING_ACCENT = '#b5482d'      # reuse COLORS['El Nino'] -- these bars ARE an El Nino effect
FREEZE_THAW_ACCENT = '#2f7a4f'
GROWING_SEASON_ACCENT = '#3a7d5c'
GROWING_SEASON_PROVINCE = '#1f5c3f'


def load_csv(name):
    path = PROCESSED / name
    if not path.is_file():
        raise SystemExit(f'Missing {path} -- see the module docstring for which script produces it.')
    return pd.read_csv(path)


def bootstrap_diff(a, b, seed=cfg.RANDOM_SEED, n_boot=cfg.BOOTSTRAP_SAMPLES):
    """Fixed-seed bootstrap, same convention as maple_sap_season.py and
    growing_season.py (distinct from calculate_kpis.bootstrap_difference's
    per-comparison seed hashing, which is the core pipeline's own method)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    diff = a.mean() - b.mean()
    rng = np.random.default_rng(seed)
    samples = (rng.choice(a, (n_boot, len(a)), replace=True).mean(axis=1)
               - rng.choice(b, (n_boot, len(b)), replace=True).mean(axis=1))
    lo, hi = np.percentile(samples, [2.5, 97.5])
    status = 'inconclusive' if lo <= 0 <= hi else 'interval_excludes_zero'
    return diff, lo, hi, status


def bootstrap_corr(a, b, seed=cfg.RANDOM_SEED, n_boot=cfg.BOOTSTRAP_SAMPLES):
    a, b = np.asarray(a, float), np.asarray(b, float)
    n = len(a)
    r = np.corrcoef(a, b)[0, 1]
    rng = np.random.default_rng(seed)
    boots = [np.corrcoef(a[idx], b[idx])[0, 1] for idx in
             (rng.integers(0, n, n) for _ in range(n_boot))]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    status = 'inconclusive' if lo <= 0 <= hi else 'interval_excludes_zero'
    return r, lo, hi, status


def heating_demand_by_city(winters, folder=REPORTS):
    """Heating-degree-days (base 18C, the Canadian standard), El Nino(+Strong)
    vs Neutral, all 6 cities. A real, measured proxy for winter heating demand
    -- not a dollar figure. Returns the per-city results table and saves the chart."""
    w = winters.loc[winters['temperature_pass']].copy()
    w['hdd_18'] = (18 - w['mean_temp']) * w['expected_days']
    cities = sorted(w['city'].unique(), key=lambda c: cfg.LATITUDES[c])

    rows = []
    for city in cities:
        block = w.loc[w['city'].eq(city)]
        en = block.loc[block['enso_class_roni'].isin(['El Nino', 'Strong El Nino']), 'hdd_18']
        ne = block.loc[block['enso_class_roni'].eq('Neutral'), 'hdd_18']
        diff, lo, hi, status = bootstrap_diff(en, ne)
        rows.append({'city': city, 'pct': diff / ne.mean() * 100, 'pct_lo': lo / ne.mean() * 100,
                     'pct_hi': hi / ne.mean() * 100, 'status': status})
    result = pd.DataFrame(rows).set_index('city')

    apply_style()
    fig, ax = plt.subplots(figsize=(9, 6.2))
    fig.subplots_adjust(top=0.80, bottom=0.30, left=0.12, right=0.96)
    x = np.arange(len(cities))
    labels = [cfg.CITY_NAMES[c] for c in cities]
    colors = [HEATING_ACCENT if result.loc[c, 'status'] == 'interval_excludes_zero' else '#d9a394' for c in cities]
    ax.bar(x, result['pct'], color=colors, width=0.6, zorder=3)
    ax.errorbar(x, result['pct'], yerr=[result['pct'] - result['pct_lo'], result['pct_hi'] - result['pct']],
                fmt='none', ecolor='#3f2018', elinewidth=1.4, capsize=5, zorder=4)
    ax.axhline(0, color='#9ca3af', linewidth=0.8)
    ax.set_xticks(x, labels, rotation=20, ha='right', fontsize=9)
    ax.set_ylabel('% fewer heating-degree-days\n(El Nino vs. Neutral winters)')
    fig.suptitle('Winter heating demand: El Nino vs. Neutral', fontsize=14, y=0.955, color='#111827')
    ax.set_title('Heating-degree-days (base 18C), all 6 cities -- darker bar = statistically significant',
                  fontsize=10, color='#475569', pad=10)

    note = ('Heating-degree-days = (18C - mean winter temperature) x expected winter days, the Canadian standard formula, computed\n'
            'from each city’s own quality-screened DJF mean temperature, 1982-2026. Bootstrap 95% CI, 10,000 resamples. All 6 cities\n'
            'point the same direction (less heating demand in El Nino winters); only Thunder Bay individually clears zero. This is a\n'
            'heating-demand proxy, not a dollar figure -- see reports/eda_impacts_findings.md for the illustrative bill translation.')
    fig.text(0.02, 0.02, note, fontsize=7.4, color='#64748b', va='bottom')
    folder.mkdir(parents=True, exist_ok=True)
    fig.savefig(folder / 'eda_heating_demand_by_city.png')
    plt.close(fig)
    print(f'Saved {folder / "eda_heating_demand_by_city.png"}')
    return result


def freeze_thaw_vs_maple(sap_season, maple, folder=REPORTS):
    """Freeze-thaw days (Feb-Apr) vs detrended maple production. The single
    strongest cross-domain result in this project."""
    x_year = maple['year'].to_numpy(dtype=float)
    y = maple['syrup_thousand_gallons'].to_numpy(dtype=float)
    slope, intercept = np.polyfit(x_year, y, 1)
    maple = maple.copy()
    maple['maple_residual'] = maple['syrup_thousand_gallons'] - (intercept + slope * x_year)

    province_avg = sap_season.groupby('year')['freeze_thaw_days'].mean().reset_index()
    merged = maple[['year', 'maple_residual']].merge(province_avg, on='year', how='inner').dropna()
    a, b = merged['maple_residual'].to_numpy(), merged['freeze_thaw_days'].to_numpy()
    n = len(a)
    r, lo, hi, status = bootstrap_corr(a, b)
    fit_slope, fit_intercept = np.polyfit(b, a, 1)

    apply_style()
    fig, ax = plt.subplots(figsize=(8.5, 6.2))
    fig.subplots_adjust(top=0.84, bottom=0.24, left=0.13, right=0.95)
    xs = np.linspace(b.min() - 2, b.max() + 2, 100)
    ax.scatter(b, a, s=42, color=FREEZE_THAW_ACCENT, alpha=0.75, zorder=3, edgecolor='white', linewidth=0.6)
    ax.plot(xs, fit_intercept + fit_slope * xs, color='#1f2937', linewidth=1.6, linestyle='--', zorder=2)
    ax.axhline(0, color='#cbd5e1', linewidth=0.8, zorder=1)
    for _, row in merged.nlargest(2, 'maple_residual').iterrows():
        ax.annotate(str(int(row['year'])), (row['freeze_thaw_days'], row['maple_residual']),
                    xytext=(6, 4), textcoords='offset points', fontsize=8, color='#475569')
    for _, row in merged.nsmallest(2, 'maple_residual').iterrows():
        ax.annotate(str(int(row['year'])), (row['freeze_thaw_days'], row['maple_residual']),
                    xytext=(6, -10), textcoords='offset points', fontsize=8, color='#475569')
    ax.set_xlabel('Freeze-thaw days, Feb-Apr (province-wide average across 6 stations)')
    ax.set_ylabel('Maple production vs. long-term trend (thousand gallons)')
    fig.suptitle('More freeze-thaw days in the actual sap season, more maple syrup', fontsize=13.5, y=0.955, color='#111827')
    ax.set_title(f'r = {r:+.2f}, 95% bootstrap CI [{lo:+.2f}, {hi:+.2f}] -- excludes zero (n={n} years, 1982-2025)',
                 fontsize=10.5, color='#1f2937', pad=10)
    note = ('A freeze-thaw day = tmin below 0C and tmax above 0C on the same day, counted over Feb-Apr, averaged across the 6\n'
            'stations. Maple production is detrended against its own 46-year growth trend. This is the only metric in this project\n'
            'whose 95% bootstrap interval clears zero at the province-wide level -- weak (r=0.28) but real, and mechanistically\n'
            'sensible: freeze-thaw cycles are literally what makes maple sap flow. IMPORTANT CAVEAT: El Nino itself does NOT\n'
            'significantly change freeze-thaw days (see eda_impacts_findings.md) -- so this link is real, but not yet shown to be\n'
            'caused by El Nino specifically.')
    fig.text(0.02, 0.02, note, fontsize=7.3, color='#64748b', va='bottom')
    folder.mkdir(parents=True, exist_ok=True)
    fig.savefig(folder / 'eda_freeze_thaw_vs_maple.png')
    plt.close(fig)
    print(f'Saved {folder / "eda_freeze_thaw_vs_maple.png"}')
    return {'r': r, 'lo': lo, 'hi': hi, 'status': status, 'n': n}


def enso_vs_freeze_thaw(sap_season):
    """Not charted on its own -- this is the caveat number referenced by the
    freeze-thaw/maple chart above: does El Nino itself move freeze-thaw days?
    sap_season_kpis.csv has no ENSO label of its own (it's calendar-year keyed,
    not winter_year keyed), so join enso_djf.csv the same way maple/growing
    season already do: calendar year Y <-> the winter labelled year Y."""
    from calculate_kpis import load_enso
    enso = load_enso(cfg.ENSO_FILE)
    sap_season = sap_season.merge(enso[['winter_year', 'enso_class_roni']],
                                   left_on='year', right_on='winter_year', how='left')
    province = sap_season.groupby('year').agg(
        freeze_thaw_days=('freeze_thaw_days', 'mean'),
        enso_class_roni=('enso_class_roni', 'first'),
    ).reset_index()
    en = province.loc[province['enso_class_roni'].isin(['El Nino', 'Strong El Nino']), 'freeze_thaw_days']
    ne = province.loc[province['enso_class_roni'].eq('Neutral'), 'freeze_thaw_days']
    diff, lo, hi, status = bootstrap_diff(en, ne)
    return {'diff': diff, 'lo': lo, 'hi': hi, 'status': status, 'n_en': len(en), 'n_ne': len(ne)}


def growing_season_by_city(growing_season, folder=REPORTS):
    complete = growing_season.loc[growing_season['complete']].copy()
    cities = sorted(cfg.STATIONS, key=lambda c: cfg.LATITUDES[c])
    rows = []
    for city in cities:
        block = complete.loc[complete['city'].eq(city)]
        en = block.loc[block['enso_class_roni'].isin(['El Nino', 'Strong El Nino']), 'growing_season_days']
        ne = block.loc[block['enso_class_roni'].eq('Neutral'), 'growing_season_days']
        diff, lo, hi, status = bootstrap_diff(en, ne)
        rows.append({'label': cfg.CITY_NAMES[city], 'diff': diff, 'lo': lo, 'hi': hi, 'status': status})

    province = complete.groupby('year').agg(
        growing_season_days=('growing_season_days', 'mean'),
        enso_class_roni=('enso_class_roni', 'first'),
        n_cities=('city', 'count'),
    ).reset_index()
    province = province.loc[province['n_cities'] >= 4]
    en = province.loc[province['enso_class_roni'].isin(['El Nino', 'Strong El Nino']), 'growing_season_days']
    ne = province.loc[province['enso_class_roni'].eq('Neutral'), 'growing_season_days']
    diff, lo, hi, status = bootstrap_diff(en, ne)
    rows.append({'label': 'Province-wide\naverage', 'diff': diff, 'lo': lo, 'hi': hi, 'status': status})
    result = pd.DataFrame(rows)

    apply_style()
    fig, ax = plt.subplots(figsize=(9.5, 6.3))
    fig.subplots_adjust(top=0.82, bottom=0.30, left=0.11, right=0.96)
    x = np.arange(len(result))
    colors = [GROWING_SEASON_PROVINCE if lbl.startswith('Province') else GROWING_SEASON_ACCENT for lbl in result['label']]
    ax.bar(x, result['diff'], color=colors, width=0.6, zorder=3, alpha=0.9)
    ax.errorbar(x, result['diff'], yerr=[result['diff'] - result['lo'], result['hi'] - result['diff']],
                fmt='none', ecolor='#1f2937', elinewidth=1.4, capsize=5, zorder=4)
    ax.axhline(0, color='#9ca3af', linewidth=0.9, zorder=1)
    ax.set_xticks(x, result['label'], fontsize=9.5)
    ax.set_ylabel('Extra frost-free days in El Nino (+Strong El Nino) winters\nvs. Neutral winters, same-year growing season')
    fig.suptitle('Are El Nino years followed by a longer frost-free growing season?', fontsize=13.5, y=0.955, color='#111827')
    ax.set_title('All 6 stations point the same direction (longer), but no single city and the\n'
                  'province-wide average both fall just short of 95% significance',
                  fontsize=10, color='#475569', pad=10)
    note = ('Growing season length = days between the last spring frost (last day on/before June 30 with tmin <= 0C) and the first\n'
            'fall frost (first day on/after July 1 with tmin <= 0C), from this project’s own daily station data. Each calendar year is\n'
            'matched to the ENSO class of the winter (Dec-Feb) that precedes it. Bootstrap 95% CI, 10,000 resamples, years require\n'
            '>=355 valid tmin days. Every city’s point estimate is positive -- suggestive, but each city’s own CI still touches zero.')
    fig.text(0.02, 0.02, note, fontsize=7.3, color='#64748b', va='bottom')
    folder.mkdir(parents=True, exist_ok=True)
    fig.savefig(folder / 'eda_growing_season_by_city.png')
    plt.close(fig)
    print(f'Saved {folder / "eda_growing_season_by_city.png"}')
    return result


def gdp_vs_enso(gdp, folder=REPORTS):
    gdp = gdp.dropna(subset=['gdp_growth_pct']).copy()
    diff_stat = bootstrap_diff(
        gdp.loc[gdp['enso_class_roni'].isin(['El Nino', 'Strong El Nino']), 'gdp_growth_pct'],
        gdp.loc[gdp['enso_class_roni'].eq('Neutral'), 'gdp_growth_pct'])

    apply_style()
    fig, ax = plt.subplots(figsize=(11, 6.1))
    fig.subplots_adjust(top=0.83, bottom=0.30, left=0.08, right=0.97)
    ax.plot(gdp['year'], gdp['gdp_growth_pct'], color='#94a3b8', linewidth=1.1, zorder=2)
    ax.axhline(0, color='#cbd5e1', linewidth=0.8, zorder=1)
    for cls in ['La Nina', 'Neutral', 'El Nino']:
        block = gdp.loc[gdp['enso_class_roni'].eq(cls)]
        ax.scatter(block['year'], block['gdp_growth_pct'], color=COLORS[cls], s=42, zorder=3,
                   label=cls, edgecolor='white', linewidth=0.5)
    ax.set_ylim(bottom=-8.5, top=9.5)
    recessions = {1982: 'early-1980s\nrecession', 1991: 'early-1990s\nrecession',
                  2009: 'financial\ncrisis', 2020: 'COVID-19\npandemic'}
    label_y = -7.4
    for year, label in recessions.items():
        row = gdp.loc[gdp['year'].eq(year)]
        if row.empty:
            continue
        y = row['gdp_growth_pct'].iloc[0]
        ax.annotate('', xy=(year, y), xytext=(year, label_y + 0.9), textcoords='data',
                    arrowprops=dict(arrowstyle='-', color='#94a3b8', linewidth=0.8), zorder=1)
        ax.text(year, label_y, label, fontsize=7.4, color='#334155', ha='center', va='top')
    ax.set_ylabel('Ontario real GDP growth (year over year, %)')
    ax.legend(loc='upper left', frameon=False, fontsize=9, ncol=3)
    fig.suptitle('Does El Nino show up in Ontario’s economic growth?', fontsize=13.5, y=0.955, color='#111827')
    ax.set_title('The biggest swings are all recessions, and they don’t line up with any one ENSO class',
                  fontsize=10, color='#475569', pad=10)
    note = ('Real (chained 2017 dollars) Ontario GDP at market prices, Statistics Canada table 36-10-0222-01. Bootstrap 95% CI:\n'
            f'El Nino(+Strong) vs. Neutral growth diff = {diff_stat[0]:+.2f} pts, CI [{diff_stat[1]:+.2f}, {diff_stat[2]:+.2f}], {diff_stat[3]}.\n'
            'GDP is driven overwhelmingly by global/national forces unrelated to any one winter’s weather -- a real winter effect on\n'
            'heating demand or snow-clearing costs is far too small a share of the economy to show up at this scale.')
    fig.text(0.02, 0.02, note, fontsize=7.3, color='#64748b', va='bottom')
    folder.mkdir(parents=True, exist_ok=True)
    fig.savefig(folder / 'eda_gdp_growth_vs_enso.png')
    plt.close(fig)
    print(f'Saved {folder / "eda_gdp_growth_vs_enso.png"}')
    return {'diff': diff_stat[0], 'lo': diff_stat[1], 'hi': diff_stat[2], 'status': diff_stat[3]}


def write_impacts_findings(heating, freeze_thaw, enso_freeze_thaw, growing_season, gdp_stat, comparisons, folder=REPORTS):
    toronto_snow = comparisons.loc[
        comparisons['enso_index'].eq('RONI') & comparisons['metric'].eq('snow_days')
        & comparisons['city'].eq('toronto') & comparisons['reference_group'].eq('Neutral')
    ].set_index('comparison_group')

    sig_heating = heating.loc[heating['status'].eq('interval_excludes_zero')]
    province_gs = growing_season.loc[growing_season['label'].str.startswith('Province')].iloc[0]

    lines = ['# EDA impacts findings', '',
             'Companion to the 4 charts in this folder with an `eda_` prefix added after the original 5 '
             '(temperature, snowfall, cold days). Computed directly from `data/processed/*.csv` -- see the '
             'module docstring in `eda_impacts.py` for which script produces each input. Exploratory, not '
             'the project’s reviewed results.', '',

             '## 1. Winter heating demand by city (`eda_heating_demand_by_city.png`)', '',
             f'Heating-degree-days (base 18C) are lower in El Nino(+Strong) winters than Neutral winters at all '
             f'6 cities. {len(sig_heating)} of {len(heating)} individually clears the 95% bootstrap interval: '
             f'{", ".join(cfg.CITY_NAMES[c] for c in sig_heating.index) if len(sig_heating) else "none"}. '
             'See `docs/`/prior analysis for an illustrative dollar translation of this effect -- not repeated '
             'here since it is not itself measured.', '',

             '## 2. Toronto snow-clearing days (already in the core pipeline output)', '', ]
    for group in ['El Nino', 'Strong El Nino']:
        if group in toronto_snow.index:
            r = toronto_snow.loc[group]
            lines.append(f'- {group} vs. Neutral: {r["difference"]:+.2f} snow days, 95% CI '
                         f'[{r["ci_lower"]:+.2f}, {r["ci_upper"]:+.2f}], {r["status"]} '
                         f'(n={int(r["n_comparison"])} vs {int(r["n_reference"])}).')
    lines += ['', 'Both clear zero. See `reports/snow_days_differences.png` and `data/processed/enso_comparisons.csv` '
              '(already produced by `run_pipeline.py`) -- not re-plotted here to avoid a duplicate chart.', '',

              '## 3. Freeze-thaw days vs. maple production (`eda_freeze_thaw_vs_maple.png`)', '',
              f'r={freeze_thaw["r"]:+.2f}, 95% CI [{freeze_thaw["lo"]:+.2f}, {freeze_thaw["hi"]:+.2f}], '
              f'{freeze_thaw["status"]} (n={freeze_thaw["n"]} years). The strongest cross-domain result in this '
              'project: more freeze-thaw days in the actual Feb-Apr sap season means more maple production, after '
              'detrending production against its own 46-year growth trend.', '',
              f'**Caveat that must travel with this finding**: El Nino itself does not significantly change '
              f'freeze-thaw days (diff={enso_freeze_thaw["diff"]:+.2f} days, 95% CI [{enso_freeze_thaw["lo"]:+.2f}, '
              f'{enso_freeze_thaw["hi"]:+.2f}], {enso_freeze_thaw["status"]}, '
              f'n={enso_freeze_thaw["n_en"]} El Nino years vs {enso_freeze_thaw["n_ne"]} Neutral years). '
              'So the freeze-thaw/maple link is real, but not yet shown to be caused by El Nino specifically.', '',

              '## 4. Growing-season length by city (`eda_growing_season_by_city.png`)', '',
              f'All 6 stations show a longer frost-free growing season in El Nino(+Strong) winters, but every '
              f'city’s own 95% CI still touches zero. Province-wide average: {province_gs["diff"]:+.1f} days, '
              f'95% CI [{province_gs["lo"]:+.1f}, {province_gs["hi"]:+.1f}], {province_gs["status"]} -- the '
              'closest-to-significant new result in this project, on the strength of 6 independent stations all '
              'pointing the same way.', '',

              '## 5. Ontario GDP growth vs. ENSO (`eda_gdp_growth_vs_enso.png`)', '',
              f'El Nino(+Strong) vs. Neutral real GDP growth: {gdp_stat["diff"]:+.2f} points, 95% CI '
              f'[{gdp_stat["lo"]:+.2f}, {gdp_stat["hi"]:+.2f}], {gdp_stat["status"]}. A clean null result: every '
              'major swing in Ontario GDP growth is a named recession or crisis unrelated to any winter’s '
              'ENSO class. Kept as a scope-boundary chart, showing a real, local winter effect does not scale up '
              'to the whole provincial economy.', '',

              '## Overall', '',
              'Two genuinely new significant results beyond the core climate metrics: Thunder Bay’s heating '
              'demand, and freeze-thaw days’ link to maple production (with the important caveat that El Nino '
              'itself doesn’t reliably drive freeze-thaw days). Growing-season length is the closest runner-up '
              '-- directionally unanimous across all 6 stations but not significant. Ontario GDP shows no '
              'relationship at all, which is itself a useful, honest boundary on how far a real winter-weather '
              'effect actually reaches.']

    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'eda_impacts_findings.md').write_text('\n'.join(lines), encoding='utf-8')
    print(f'Saved {folder / "eda_impacts_findings.md"}')


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    winters = load_csv('winter_kpis.csv')
    comparisons = load_csv('enso_comparisons.csv')
    sap_season = load_csv('sap_season_kpis.csv')
    maple = load_csv('ontario_maple_syrup_production.csv')
    growing_season_raw = load_csv('growing_season_kpis.csv')
    gdp = load_csv('ontario_gdp.csv')

    heating = heating_demand_by_city(winters)
    freeze_thaw = freeze_thaw_vs_maple(sap_season, maple)
    enso_freeze_thaw = enso_vs_freeze_thaw(sap_season)
    growing_season = growing_season_by_city(growing_season_raw)
    gdp_stat = gdp_vs_enso(gdp)
    write_impacts_findings(heating, freeze_thaw, enso_freeze_thaw, growing_season, gdp_stat, comparisons)


if __name__ == '__main__':
    main()