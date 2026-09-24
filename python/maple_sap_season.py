"""Recompute winter-style KPIs over the actual maple sap season (Feb-Apr) instead
of this project's defined DJF winter, and check them against maple production.

This is a standalone exploratory script, not part of run_pipeline.py: it uses a
different season window and calendar-year keying than the rest of the validated
pipeline, so it is kept separate rather than bent into winter_kpis.csv's shape.

Run directly:

    python maple_sap_season.py

Writes data/processed/sap_season_kpis.csv and prints the same bootstrap
correlation check already run for the DJF window, for direct comparison.
"""
import numpy as np
import pandas as pd
import config as cfg
from clean_data import clean_station, spring_reports

SAP_SEASON_MONTHS = (2, 3, 4)  # February-April
BASELINE_START, BASELINE_END = cfg.BASELINE_START, cfg.BASELINE_END


def build_sap_season_kpis(input_dir=None):
    """input_dir lets run_pipeline.py pass its own --input-dir through instead
    of always reading cfg.INPUT_DIR -- standalone use still defaults to it."""
    input_dir = input_dir or cfg.INPUT_DIR
    frames = []
    for city in cfg.STATIONS:
        path = input_dir / f'{city}_daily.csv'
        daily, _review, _profile = clean_station(path, city, cfg.DERIVE_MISSING_MEAN)
        _monthly, seasons, _absent = spring_reports(daily, city, cfg.FIRST_WINTER, cfg.LAST_WINTER,
                                                     months=SAP_SEASON_MONTHS)
        frames.append(seasons)
    result = pd.concat(frames, ignore_index=True)

    baselines = (result.loc[result['year'].between(BASELINE_START, BASELINE_END) & result['temperature_pass']]
                 .groupby('city')['mean_temp'].mean().rename('baseline_mean_temp'))
    result = result.merge(baselines, on='city', how='left')
    result['temp_anomaly'] = result['mean_temp'] - result['baseline_mean_temp']
    return result


def bootstrap_corr(a, b, seed=20260921, n_boot=10000):
    a, b = np.asarray(a, float), np.asarray(b, float)
    n = len(a)
    r = np.corrcoef(a, b)[0, 1]
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        boots.append(np.corrcoef(a[idx], b[idx])[0, 1])
    lo, hi = np.percentile(boots, [2.5, 97.5])
    status = 'inconclusive' if lo <= 0 <= hi else 'interval_excludes_zero'
    return r, lo, hi, status


def main():
    seasons = build_sap_season_kpis()
    out_path = cfg.ROOT / 'data' / 'processed' / 'sap_season_kpis.csv'
    seasons.to_csv(out_path, index=False, float_format='%.10g')
    print(f'Wrote {out_path} ({len(seasons)} rows, {SAP_SEASON_MONTHS[0]}-{SAP_SEASON_MONTHS[-1]} season)')

    maple_path = cfg.ROOT / 'data' / 'processed' / 'ontario_maple_syrup_production.csv'
    maple = pd.read_csv(maple_path)
    x = maple['year'].to_numpy(dtype=float)
    y = maple['syrup_thousand_gallons'].to_numpy(dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    maple['maple_residual'] = maple['syrup_thousand_gallons'] - (intercept + slope * x)

    metrics = ['temp_anomaly', 'snowfall_total_cm', 'snow_days', 'days_below_m20', 'freeze_thaw_days']
    province_avg = seasons.groupby('year')[metrics].mean().reset_index()

    print(f'\nSap season ({SAP_SEASON_MONTHS[0]}-{SAP_SEASON_MONTHS[-1]}) vs. detrended maple production, '
          'province-wide average, bootstrap 95% CI:')
    for metric in metrics:
        merged = maple[['year', 'maple_residual']].merge(
            province_avg[['year', metric]], on='year', how='inner').dropna()
        r, lo, hi, status = bootstrap_corr(merged['maple_residual'], merged[metric])
        print(f'  {metric:20s} n={len(merged):3d}  r={r:+.2f}  95% CI=[{lo:+.2f}, {hi:+.2f}]  {status}')


if __name__ == '__main__':
    main()