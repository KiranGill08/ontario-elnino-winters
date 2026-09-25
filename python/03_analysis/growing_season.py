"""Growing-season length (frost-free period) vs ENSO -- computed entirely from
this project's own daily station data, no external dataset needed.

Definition (standard agroclimatology): for each city and calendar year,
  - last spring frost = last day on/before June 30 with tmin <= 0C
  - first fall frost   = first day on/after July 1 with tmin <= 0C
  - growing season length = (first fall frost date - last spring frost date) in days

This is the same metric StatCan/ECCC use for frost-free period length, and it's a
genuine, commonly-used indicator of the growing season available to trees, crops
and gardens -- longer season = more growth potential, all else equal.

ENSO classification: each calendar year Y is matched to this project's winter_year Y
label (the DJF ending in February of that year), the same convention already used
for the maple sap season (Feb-Apr of year Y co-occurs with the winter labelled year Y).

This is a standalone exploratory script, not part of run_pipeline.py: it uses a
different calendar-year keying than the rest of the validated pipeline, so it is
kept separate rather than bent into winter_kpis.csv's shape (same rationale as
maple_sap_season.py).

Run directly:

    python growing_season.py

Writes data/processed/growing_season_kpis.csv and prints the bootstrap
significance checks used in eda_impacts.py.
"""
import numpy as np
import pandas as pd
import sys
from pathlib import Path
# Let this script find config.py and the modules in the numbered subfolders.
_PY = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(_PY)] + sorted(str(p) for p in _PY.iterdir() if p.is_dir() and p.name[:2].isdigit())
import config as cfg
from clean_data import clean_station
from calculate_kpis import load_enso

MIN_VALID_DAYS = 355  # out of ~365; require a nearly-complete year to trust frost dates


def first_and_last_frost(year_df, year):
    """Return (last_spring_frost_date, first_fall_frost_date, n_valid_tmin) for one city-year."""
    d = year_df.set_index('date')
    full_idx = pd.date_range(f'{year}-01-01', f'{year}-12-31', freq='D')
    tmin = d['tmin'].reindex(full_idx)
    n_valid = tmin.notna().sum()

    mid = pd.Timestamp(f'{year}-07-01')
    spring = tmin.loc[:mid - pd.Timedelta(days=1)]
    fall = tmin.loc[mid:]

    spring_frosts = spring.index[spring <= 0]
    fall_frosts = fall.index[fall <= 0]
    last_spring = spring_frosts.max() if len(spring_frosts) else pd.NaT
    first_fall = fall_frosts.min() if len(fall_frosts) else pd.NaT
    return last_spring, first_fall, n_valid


def build_growing_season_kpis(input_dir=None):
    """input_dir lets run_pipeline.py pass its own --input-dir through instead
    of always reading cfg.INPUT_DIR -- standalone use still defaults to it."""
    input_dir = input_dir or cfg.INPUT_DIR
    rows = []
    for city in cfg.STATIONS:
        path = input_dir / f'{city}_daily.csv'
        clean, _review, _profile = clean_station(path, city, cfg.DERIVE_MISSING_MEAN)
        for year in range(cfg.FIRST_WINTER, 2026):  # calendar years with a full year of data
            year_df = clean.loc[clean['date'].dt.year.eq(year), ['date', 'tmin']]
            last_spring, first_fall, n_valid = first_and_last_frost(year_df, year)
            complete = n_valid >= MIN_VALID_DAYS and pd.notna(last_spring) and pd.notna(first_fall)
            length = (first_fall - last_spring).days if complete else np.nan
            rows.append({
                'city': city, 'year': year,
                'last_spring_frost': last_spring, 'first_fall_frost': first_fall,
                'growing_season_days': length, 'n_valid_tmin_days': int(n_valid),
                'complete': complete,
            })
    result = pd.DataFrame(rows)
    enso = load_enso(cfg.ENSO_FILE)
    result = result.merge(enso[['winter_year', 'enso_class_oni', 'enso_class_roni']],
                           left_on='year', right_on='winter_year', how='left').drop(columns='winter_year')
    return result


def bootstrap_diff(a, b, seed=cfg.RANDOM_SEED, n_boot=cfg.BOOTSTRAP_SAMPLES):
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
    boots = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        boots.append(np.corrcoef(a[idx], b[idx])[0, 1])
    lo, hi = np.percentile(boots, [2.5, 97.5])
    status = 'inconclusive' if lo <= 0 <= hi else 'interval_excludes_zero'
    return r, lo, hi, status


def main():
    gs = build_growing_season_kpis()
    out_path = cfg.ROOT / 'data' / 'processed' / 'growing_season_kpis.csv'
    gs.to_csv(out_path, index=False, float_format='%.10g')
    print(f'Wrote {out_path} ({len(gs)} rows)')
    print(f'Complete city-years: {gs["complete"].sum()} / {len(gs)}')
    print(gs.groupby('city')['complete'].mean().round(2))

    complete = gs.loc[gs['complete']].copy()

    print('\n--- Per-city: growing season length, El Nino(+Strong) vs Neutral ---')
    for city in cfg.STATIONS:
        block = complete.loc[complete['city'].eq(city)]
        en = block.loc[block['enso_class_roni'].isin(['El Nino', 'Strong El Nino']), 'growing_season_days']
        ne = block.loc[block['enso_class_roni'].eq('Neutral'), 'growing_season_days']
        if len(en) < 3 or len(ne) < 3:
            print(f'  {city:10s} insufficient n (en={len(en)}, ne={len(ne)})')
            continue
        diff, lo, hi, status = bootstrap_diff(en, ne)
        print(f'  {city:10s} en_mean={en.mean():.1f} (n={len(en)})  ne_mean={ne.mean():.1f} (n={len(ne)})  '
              f'diff={diff:+.1f} days  95% CI=[{lo:+.1f}, {hi:+.1f}]  {status}')

    print('\n--- Province-wide average: growing season length, El Nino(+Strong) vs Neutral ---')
    province = complete.groupby('year').agg(
        growing_season_days=('growing_season_days', 'mean'),
        enso_class_roni=('enso_class_roni', 'first'),
        n_cities=('city', 'count'),
    ).reset_index()
    province = province.loc[province['n_cities'] >= 4]  # require most cities present that year
    en = province.loc[province['enso_class_roni'].isin(['El Nino', 'Strong El Nino']), 'growing_season_days']
    ne = province.loc[province['enso_class_roni'].eq('Neutral'), 'growing_season_days']
    diff, lo, hi, status = bootstrap_diff(en, ne)
    print(f'  province    en_mean={en.mean():.1f} (n={len(en)})  ne_mean={ne.mean():.1f} (n={len(ne)})  '
          f'diff={diff:+.1f} days  95% CI=[{lo:+.1f}, {hi:+.1f}]  {status}')

    print('\n--- Correlation with winter DJF temp anomaly (same ENSO-adjacent winter) ---')
    winter = pd.read_csv(cfg.ROOT / 'data' / 'processed' / 'winter_kpis.csv')
    winter = winter.loc[winter['temperature_pass']].rename(columns={'winter_year': 'year'})
    merged = complete.merge(winter[['city', 'year', 'temp_anomaly']], on=['city', 'year'], how='inner').dropna(
        subset=['growing_season_days', 'temp_anomaly'])
    r, lo, hi, status = bootstrap_corr(merged['growing_season_days'], merged['temp_anomaly'])
    print(f'  per city-year  n={len(merged)}  r={r:+.2f}  95% CI=[{lo:+.2f}, {hi:+.2f}]  {status}')


if __name__ == '__main__':
    main()