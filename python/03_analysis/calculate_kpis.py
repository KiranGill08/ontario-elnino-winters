"""Calculate winter KPIs, station baselines, ENSO groups and comparisons."""
import hashlib
import numpy as np
import pandas as pd
import config as cfg


# Divide the ENSO index values into three classes, plus a strong El Nino flag.
def classify(values):
    result = pd.Series('Neutral', index=values.index, dtype='string')
    result.loc[values >= cfg.EL_NINO_THRESHOLD] = 'El Nino'
    result.loc[values <= cfg.LA_NINA_THRESHOLD] = 'La Nina'
    return result.mask(values.isna())


#Load the ENSO table and classify each winter into El Nino, La Nina, or Neutral.
def load_enso(path):
    enso = pd.read_csv(path)
    required = ['winter_year', 'oni_djf', 'roni_djf']
    if not set(required).issubset(enso.columns):
        raise ValueError(f'ENSO input needs {required}')
    for column in required:
        enso[column] = pd.to_numeric(enso[column], errors='raise')
    if enso['winter_year'].duplicated().any():
        raise ValueError('Duplicate ENSO winter years')
    enso = enso.set_index('winter_year').reindex(range(cfg.FIRST_WINTER, cfg.LAST_WINTER + 1))
    if enso[['oni_djf', 'roni_djf']].isna().any().any():
        raise ValueError('Every requested winter must have ONI and RONI values')
    for name in ['oni', 'roni']:
        enso[f'enso_class_{name}'] = classify(enso[f'{name}_djf'])
        enso[f'strong_el_nino_{name}'] = enso[f'{name}_djf'] >= cfg.STRONG_THRESHOLD
    return enso.reset_index()

#add city names, regions, and latitude to a DataFrame of winters or comparisons.
def add_metadata(frame):
    result = frame.copy()
    result['city_name'] = result['city'].map(cfg.CITY_NAMES)
    result['region'] = result['city'].map(cfg.REGIONS)
    result['latitude_approx'] = result['city'].map(cfg.LATITUDES)
    result['included_in_proposal'] = result['city'].isin(cfg.PRIMARY_STATIONS)
    result['included_in_repo_study'] = result['city'].isin(cfg.REPO_STATIONS)
    return result

#wrap winter KPIs with baseline calculations, ENSO values, and detrended residuals.
def winter_kpis(winters, enso):
    result = winters.copy()
    selected = result.loc[result['winter_year'].between(cfg.BASELINE_START, cfg.BASELINE_END)]
    baselines = selected.groupby('city').agg(
        baseline_mean_temp=('mean_temp', 'mean'), baseline_n_winters=('mean_temp', 'count'))
    baselines['baseline_start_winter'] = cfg.BASELINE_START
    baselines['baseline_end_winter'] = cfg.BASELINE_END
    baselines['baseline_complete'] = baselines['baseline_n_winters'].eq(cfg.BASELINE_END - cfg.BASELINE_START + 1)
    baselines['baseline_status'] = np.select(
        [baselines['baseline_n_winters'].eq(0), baselines['baseline_complete']],
        ['unavailable', 'complete'], default='partial_available_winter_average')
    result = result.merge(baselines.reset_index(), on='city', validate='many_to_one')
    result['temp_anomaly'] = result['mean_temp'] - result['baseline_mean_temp']
    result['winter_label'] = (result['winter_year'] - 1).astype(str) + '-' + result['winter_year'].astype(str).str[-2:]
    result['winter_start'] = pd.to_datetime((result['winter_year'] - 1).astype(str) + '-12-01')
    result['winter_end'] = pd.to_datetime(result['winter_year'].astype(str) + '-03-01') - pd.Timedelta(days=1)
    result['temperature_coverage_pct'] = result['valid_temperature_days'] / result['expected_days'] * 100
    result['snowfall_coverage_pct'] = result['valid_snowfall_days'] / result['expected_days'] * 100
    result['derived_temperature_share_pct'] = result['derived_temperature_days'].div(
        result['valid_temperature_days'].replace(0, np.nan)) * 100
    result['quality_method'] = cfg.QUALITY_METHOD
    result = result.merge(enso, on='winter_year', validate='many_to_one')
    index = cfg.PRIMARY_INDEX.lower()
    result['enso_index'] = cfg.PRIMARY_INDEX
    result['enso_value'] = result[f'{index}_djf']
    result['enso_class'] = result[f'enso_class_{index}']
    result['strong_el_nino'] = result[f'strong_el_nino_{index}']

    trends = []
    result['temp_detrended_residual'] = np.nan
    for city, block in result.groupby('city'):
        valid = block['mean_temp'].notna()
        x = block.loc[valid, 'winter_year'].to_numpy(dtype=float)
        y = block.loc[valid, 'mean_temp'].to_numpy(dtype=float)
        if len(y) >= 3:
            slope, intercept = np.polyfit(x, y, 1)
            result.loc[block.index[valid], 'temp_detrended_residual'] = y - (intercept + slope*x)
        else:
            slope = intercept = np.nan
        trends.append({'city': city, 'n_winters': len(y), 'slope_c_per_decade': slope*10,
                       'intercept': intercept, 'first_winter': x.min() if len(x) else np.nan,
                       'last_winter': x.max() if len(x) else np.nan})
    return add_metadata(result), add_metadata(baselines.reset_index()), pd.DataFrame(trends)


def bootstrap_difference(a, b, seed_key):
    """Independent resampling of entire winters in two disjoint ENSO groups."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    difference = a.mean() - b.mean() if len(a) and len(b) else np.nan
    if min(len(a), len(b)) < 2:
        return difference, np.nan, np.nan, 'insufficient_data'
    seed = int(hashlib.sha256(f'{cfg.RANDOM_SEED}:{seed_key}'.encode()).hexdigest()[:16], 16)
    rng = np.random.default_rng(seed)
    samples = []
    for start in range(0, cfg.BOOTSTRAP_SAMPLES, 1000):
        size = min(1000, cfg.BOOTSTRAP_SAMPLES - start)
        samples.append(rng.choice(a, (size, len(a)), replace=True).mean(axis=1)
                       - rng.choice(b, (size, len(b)), replace=True).mean(axis=1))
    low, high = np.percentile(np.concatenate(samples), [2.5, 97.5])
    status = 'inconclusive' if low <= 0 <= high else 'interval_excludes_zero'
    return difference, low, high, status


def group_mask(frame, index, group):
    if group == 'Strong El Nino':
        return frame[f'strong_el_nino_{index}'].eq(True)
    return frame[f'enso_class_{index}'].eq(group)


def summarize_groups(winters):
    rows = []
    for index in ['oni', 'roni']:
        for city, block in winters.groupby('city'):
            for group in cfg.CLASS_ORDER + ['Strong El Nino']:
                selected = block.loc[group_mask(block, index, group)]
                for metric in cfg.METRICS:
                    valid = selected.loc[selected[metric].notna()]
                    rows.append({'city': city, 'enso_index': index.upper(), 'enso_group': group,
                                 'metric': metric, 'unit': cfg.METRICS[metric][1],
                                 'n_group_winters': len(selected), 'n_eligible': len(valid),
                                 'mean': valid[metric].mean(), 'median': valid[metric].median(),
                                 'std': valid[metric].std(), 'min': valid[metric].min(),
                                 'max': valid[metric].max(),
                                 'eligible_years': ','.join(valid['winter_year'].astype(str))})
    return add_metadata(pd.DataFrame(rows))


def comparisons(winters, metrics=None):
    metrics = metrics or list(cfg.METRICS)
    rows = []
    pairs = [('El Nino', 'Neutral'), ('Strong El Nino', 'Neutral'),
             ('El Nino', 'La Nina'), ('La Nina', 'Neutral')]
    for index in ['oni', 'roni']:
        for city, block in winters.groupby('city'):
            for metric in metrics:
                for comparison, reference in pairs:
                    a = block.loc[group_mask(block, index, comparison) & block[metric].notna()]
                    b = block.loc[group_mask(block, index, reference) & block[metric].notna()]
                    difference, low, high, status = bootstrap_difference(
                        a[metric], b[metric], f'{index}:{city}:{metric}:{comparison}:{reference}')
                    rows.append({
                        'city': city, 'enso_index': index.upper(), 'metric': metric,
                        'comparison_group': comparison, 'reference_group': reference,
                        'comparison_mean': a[metric].mean(), 'reference_mean': b[metric].mean(),
                        'difference': difference, 'ci_lower': low, 'ci_upper': high,
                        'status': status, 'n_comparison': len(a), 'n_reference': len(b),
                        'comparison_years': ','.join(a['winter_year'].astype(str)),
                        'reference_years': ','.join(b['winter_year'].astype(str)),
                        'bootstrap_samples': cfg.BOOTSTRAP_SAMPLES,
                        'sample_note': 'fewer_than_10_winters_in_a_group' if min(len(a), len(b)) < 10 else '',
                        'quality_method': cfg.QUALITY_METHOD,
                    })
    return add_metadata(pd.DataFrame(rows))


def regional_comparisons(winters):
    """Compare north-minus-south ENSO differences using common winters.

    Pair cities within each winter before bootstrap resampling. This preserves
    shared weather-year dependence. No province-wide geographic mean is made.
    """
    rows = []
    north = 'thunderbay'
    for south in ['windsor', 'toronto']:
        if not {north, south}.issubset(set(winters['city'])):
            continue
        for index in ['oni', 'roni']:
            for metric in cfg.METRICS:
                a = winters.loc[winters['city'].eq(north), ['winter_year', metric, f'enso_class_{index}']]
                b = winters.loc[winters['city'].eq(south), ['winter_year', metric]]
                common = a.merge(b, on='winter_year', suffixes=('_north', '_south'), validate='one_to_one').dropna()
                common['north_minus_south'] = common[f'{metric}_north'] - common[f'{metric}_south']
                en = common.loc[common[f'enso_class_{index}'].eq('El Nino')]
                neutral = common.loc[common[f'enso_class_{index}'].eq('Neutral')]
                difference, low, high, status = bootstrap_difference(
                    en['north_minus_south'], neutral['north_minus_south'], f'regional:{index}:{south}:{metric}')
                rows.append({'north_city': north, 'south_city': south, 'enso_index': index.upper(), 'metric': metric,
                             'difference_of_differences': difference, 'ci_lower': low, 'ci_upper': high,
                             'status': status, 'n_common_el_nino': len(en), 'n_common_neutral': len(neutral),
                             'el_nino_years': ','.join(en['winter_year'].astype(str)),
                             'neutral_years': ','.join(neutral['winter_year'].astype(str))})
    return pd.DataFrame(rows)


def enrich_daily(daily, winters):
    result = daily.copy()
    result['year'] = result['date'].dt.year
    result['month'] = result['date'].dt.month
    result['is_winter'] = result['month'].isin(cfg.WINTER_MONTHS)
    result['in_study_period'] = result['is_winter'] & result['winter_year'].between(cfg.FIRST_WINTER, cfg.LAST_WINTER).fillna(False)
    result['snow_day'] = result['snowfall_cm'].ge(cfg.SNOW_DAY_CM).where(result['snowfall_cm'].notna()).astype('Int64')
    result['very_cold_day'] = result['tmin'].le(cfg.COLD_DAY_C).where(result['tmin'].notna()).astype('Int64')
    fields = ['city', 'winter_year', *cfg.METRICS, 'baseline_mean_temp', 'baseline_n_winters',
              'baseline_status', 'winter_label', 'temperature_pass', 'snowfall_pass', 'cold_days_pass',
              'enso_index', 'enso_value', 'enso_class', 'strong_el_nino', 'oni_djf', 'roni_djf',
              'enso_class_oni', 'enso_class_roni', 'strong_el_nino_oni', 'strong_el_nino_roni']
    result = result.merge(winters[fields], on=['city', 'winter_year'], how='left', validate='many_to_one')
    return add_metadata(result)
