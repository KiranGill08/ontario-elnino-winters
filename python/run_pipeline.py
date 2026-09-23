"""Run cleaning, KPI calculations, ENSO comparisons and EDA in one command."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import sys
import numpy as np
import pandas as pd
import config as cfg
from clean_data import clean_station, winter_reports
from calculate_kpis import (load_enso, winter_kpis, enrich_daily, summarize_groups,
                            comparisons, regional_comparisons, add_metadata)


def save_csv(frame, path):
    frame.to_csv(path, index=False, date_format='%Y-%m-%d', float_format='%.10g')


def validate_results(daily, winters, baselines, profiles, comparisons_table):
    assert not daily.duplicated(['city', 'date']).any(), 'Duplicate daily keys'
    assert not winters.duplicated(['city', 'winter_year']).any(), 'Duplicate winter keys'
    assert len(winters) == len(cfg.STATIONS)*(cfg.LAST_WINTER-cfg.FIRST_WINTER+1)
    assert len(daily) == sum(p['clean_rows'] for p in profiles)
    for p in profiles:
        assert p['input_rows'] == p['clean_rows'] + p['identical_duplicates_removed'] + p['quarantined_rows']
    assert winters['enso_class'].notna().all()
    assert set(winters['expected_days']).issubset({90, 91})
    valid = winters['temp_anomaly'].notna()
    assert np.allclose(winters.loc[valid, 'temp_anomaly'],
                       winters.loc[valid, 'mean_temp'] - winters.loc[valid, 'baseline_mean_temp'])
    for city, group in winters.groupby('city'):
        b = group.loc[group['winter_year'].between(cfg.BASELINE_START, cfg.BASELINE_END)]
        value = baselines.set_index('city').loc[city]
        assert b['mean_temp'].count() == value['baseline_n_winters']
        if b['temp_anomaly'].notna().any():
            assert abs(b['temp_anomaly'].mean()) < 1e-9, 'Baseline anomalies must center on zero'
    for metric, flag in [('mean_temp', 'temperature_pass'), ('temp_anomaly', 'temperature_pass'),
                         ('snowfall_total_cm', 'snowfall_pass'), ('snow_days', 'snowfall_pass'),
                         ('days_below_m20', 'cold_days_pass')]:
        assert winters.loc[~winters[flag], metric].isna().all(), f'Incomplete {metric} must be missing'
    eligible = comparisons_table['ci_lower'].notna()
    assert (comparisons_table.loc[eligible, 'ci_lower'] <= comparisons_table.loc[eligible, 'ci_upper']).all()


def findings_report(winters, baselines, comparison, regional, folder):
    lines = ['# Calculated findings', '',
             f'Primary index: {cfg.PRIMARY_INDEX}. Period: winters ending {cfg.FIRST_WINTER}–{cfg.LAST_WINTER}.', '',
             'These are historical associations. Confidence intervals assume independent winters and are not adjusted for multiple comparisons. Station changes and missing snowfall limit interpretation.', '',
             '## City baselines', '',
             '| City | Baseline mean (°C) | Eligible baseline winters | Status |',
             '|---|---:|---:|---|']
    for _, row in baselines.iterrows():
        lines.append(f'| {row.city_name} | {row.baseline_mean_temp:.3f} | {row.baseline_n_winters} | {row.baseline_status} |')
    lines += ['', 'Baseline means use eligible winters ending in 1991–2020 by default. The first baseline winter begins in December 1990. Anomalies are calculated for all eligible study winters, including those outside the baseline.', '',
              '## Main proposal locations: El Niño minus neutral', '',
              '| City | KPI | Difference | 95% interval | Group sizes | Interpretation |',
              '|---|---|---:|---|---|---|']
    selected = comparison.loc[comparison['enso_index'].eq(cfg.PRIMARY_INDEX)
        & comparison['included_in_proposal'] & comparison['comparison_group'].eq('El Nino')
        & comparison['reference_group'].eq('Neutral') & comparison['metric'].ne('temp_anomaly')]
    for _, row in selected.iterrows():
        label, unit = cfg.METRICS[row.metric]
        interval = f'{row.ci_lower:.2f} to {row.ci_upper:.2f}' if np.isfinite(row.ci_lower) else 'Unavailable'
        lines.append(f'| {row.city_name} | {label} | {row.difference:+.2f} {unit} | {interval} | {row.n_comparison}/{row.n_reference} | {row.status} |')
    lines += ['', 'Group sizes are comparison/reference. The temperature-anomaly difference equals the mean-temperature difference for the same city and eligible winters because the fixed baseline cancels.', '',
              '## Business-question outputs', '',
              '- BQ1: `winter_kpis.csv`, temperature group summaries and temperature comparison charts.',
              '- BQ2: snowfall totals and both El Niño–neutral and El Niño–La Niña comparisons.',
              '- BQ3: complete-winter counts of minimum temperature at or below the configured cold threshold.',
              '- BQ4: `regional_comparisons.csv` compares Thunder Bay with Windsor and Toronto on shared eligible years. Its difference is the northern ENSO difference minus the southern ENSO difference.',
              '- BQ5: complete-winter snow-day counts using the configured new-snow threshold.',
              '- BQ6: rows with `comparison_group=Strong El Nino` in `enso_comparisons.csv`, with actual group sizes.', '',
              '## Interpretation limits', '',
              '- Inconclusive means the interval includes zero; it is not proof of no association.',
              '- Temperature coverage and snowfall coverage are checked separately. Missing snowfall is never treated as zero.',
              '- London and Sudbury are included as available candidates; the proposal membership flag identifies the original four locations.',
              '- ONI and RONI results are separate. Use one index consistently in a reported result.',
              '- `temperature_trend_sensitivity.csv` compares residuals after fitting a linear trend per city. Those intervals condition on the fitted trend and do not include trend-estimation uncertainty.',
              '- The weather data cannot establish budget savings, staffing needs, total energy use or next winter’s conditions.', '']
    (folder / 'findings.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, default=cfg.INPUT_DIR)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--no-plots', action='store_true')
    args = parser.parse_args()
    cfg.validate()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')
    output = args.output_dir or cfg.ROOT / 'runs' / stamp
    output = output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error('Choose an empty output directory; existing results are preserved.')
    if args.input_dir.resolve().is_relative_to(output):
        parser.error('Output must be separate from the inputs and their parent directories.')
    paths = [args.input_dir / f'{city}_daily.csv' for city in cfg.STATIONS]
    if any(not p.is_file() for p in paths):
        parser.error('Missing CSVs: ' + ', '.join(str(p) for p in paths if not p.is_file()))
    enso = load_enso(cfg.ENSO_FILE)
    daily_frames, reviews, profiles, months, winter_frames, gaps = [], [], [], [], [], []
    for city, path in zip(cfg.STATIONS, paths):
        daily, review, profile = clean_station(path, city, cfg.DERIVE_MISSING_MEAN)
        monthly, winter, absent = winter_reports(daily, city, cfg.FIRST_WINTER, cfg.LAST_WINTER)
        daily_frames.append(daily); reviews.append(review); profiles.append(profile)
        months.append(monthly); winter_frames.append(winter); gaps.append(absent)
        print(f'Cleaned {city}: {len(daily):,} rows', flush=True)
    base_daily = pd.concat(daily_frames, ignore_index=True)
    winters, baselines, trends = winter_kpis(pd.concat(winter_frames, ignore_index=True), enso)
    daily = enrich_daily(base_daily, winters)
    groups = summarize_groups(winters)
    comparison = comparisons(winters)
    regional = regional_comparisons(winters)
    trend_sensitivity = comparisons(winters, ['temp_detrended_residual'])
    validate_results(daily, winters, baselines, profiles, comparison)
    print('KPI calculations and validation passed', flush=True)

    processed = output / 'data'
    reports = output / 'reports'
    processed.mkdir(parents=True)
    reports.mkdir()
    save_csv(daily, processed / 'all_stations_daily_enriched.csv')
    for city, block in daily.groupby('city'):
        save_csv(block, processed / f'{city}_daily_enriched.csv')
    save_csv(winters, processed / 'winter_kpis.csv')
    save_csv(baselines, processed / 'city_baselines.csv')
    save_csv(groups, processed / 'enso_group_summary.csv')
    save_csv(comparison, processed / 'enso_comparisons.csv')
    save_csv(regional, processed / 'regional_comparisons.csv')
    save_csv(trend_sensitivity, processed / 'temperature_trend_sensitivity.csv')
    save_csv(trends, processed / 'temperature_trends.csv')
    save_csv(enso, processed / 'enso_winter_labels.csv')
    save_csv(add_metadata(pd.DataFrame(profiles)), reports / 'station_profile.csv')
    save_csv(pd.concat(reviews, ignore_index=True), reports / 'records_to_review.csv')
    save_csv(pd.concat(months, ignore_index=True), reports / 'monthly_quality.csv')
    save_csv(pd.concat(gaps, ignore_index=True), reports / 'missing_winter_dates.csv')
    base_daily.groupby('city')[cfg.NUMERIC].describe().to_csv(reports / 'numeric_summary.csv')
    base_daily.groupby(['city', 'station_id']).agg(first_date=('date', 'min'), last_date=('date', 'max'),
        rows=('date', 'size')).to_csv(reports / 'station_id_coverage.csv', date_format='%Y-%m-%d')
    save_csv(winters.loc[winters['exclusion_reasons'].ne(''),
        ['city', 'winter_year', 'temperature_pass', 'snowfall_pass', 'cold_days_pass', 'exclusion_reasons']],
        reports / 'winter_exclusions.csv')
    findings_report(winters, baselines, comparison, regional, reports)
    if not args.no_plots:
        from eda import create_charts
        from extra_charts import create_extra_charts
        create_charts(daily, winters, comparison, trends, output / 'figures')
        create_extra_charts(winters, comparison, output / 'figures')
    sources = [{'file': str(p.relative_to(args.input_dir)),
                'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]
    sources.append({'file': 'enso_djf.csv', 'sha256': hashlib.sha256(cfg.ENSO_FILE.read_bytes()).hexdigest()})
    settings = {name: value for name, value in vars(cfg).items()
                if name.isupper() and isinstance(value, (str, int, float, list, dict, tuple, bool))}
    manifest = {'completed_utc': datetime.now(timezone.utc).isoformat(), 'sources': sources,
                'python': sys.version, 'pandas': pd.__version__, 'numpy': np.__version__,
                'settings': settings, 'daily_rows': len(daily), 'winter_rows': len(winters),
                'validation': 'passed'}
    (output / 'run_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(f'Finished: {output}', flush=True)


if __name__ == '__main__':
    main()