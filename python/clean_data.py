"""Read, clean and quality-screen the original CSVs without overwriting them."""
import numpy as np
import pandas as pd
from config import (COLUMNS, NUMERIC, MISSING, TEMPERATURE_SCREEN_C,
                    MAX_MONTHLY_MISSING, MAX_CONSECUTIVE_MISSING,
                    SNOW_DAY_CM, COLD_DAY_C, WINTER_MONTHS)


def longest_missing(series):
    """Count consecutive missing calendar days, including dates absent in the CSV."""
    longest = current = 0
    for missing in series.isna():
        current = current + 1 if missing else 0
        longest = max(longest, current)
    return longest


def clean_station(path, city, derive_mean=True):
    raw = pd.read_csv(path, dtype='string', keep_default_na=False)
    if list(raw.columns) != COLUMNS:
        raise ValueError(f'{path.name}: expected columns {COLUMNS}, got {list(raw.columns)}')
    if raw.empty:
        raise ValueError(f'{path.name}: file has no records')
    normalized = raw.apply(lambda s: s.str.strip())
    out = pd.DataFrame(index=raw.index)
    out['city'] = city
    out['source_file'] = path.name
    out['source_row'] = raw.index + 2
    notes = pd.Series('', index=raw.index, dtype='string')

    def flag(mask, message):
        mask = mask.fillna(False)
        notes.loc[mask] = notes.loc[mask] + message + ';'

    out['date'] = pd.to_datetime(normalized['date'], format='%Y-%m-%d', errors='coerce')
    invalid_date = out['date'].isna()
    flag(invalid_date, 'invalid_date:quarantined')
    station_ok = normalized['station_id'].str.fullmatch(r'[1-9][0-9]*').fillna(False)
    station_number = pd.to_numeric(normalized['station_id'], errors='coerce')
    station_ok &= station_number.le(2147483647)
    out['station_id'] = normalized['station_id'].where(station_ok)
    flag(~station_ok, 'invalid_station_id:quarantined')

    for column in NUMERIC:
        original = normalized[column]
        missing = original.str.lower().isin(MISSING)
        values = pd.to_numeric(original.mask(missing), errors='coerce').astype(float)
        invalid = ~missing & (values.isna() | ~np.isfinite(values))
        out[column] = values.mask(invalid)
        flag(invalid, f'{column}:unparseable_or_nonfinite:set_missing')

    # Conservative screening limits, not a claim that these are physical limits.
    for column in ['tmax', 'tmin', 'tmean']:
        bad = out[column].notna() & ~out[column].between(*TEMPERATURE_SCREEN_C)
        flag(bad, f'{column}:outside_review_range:set_missing')
        out.loc[bad, column] = np.nan
    reversed_range = out['tmin'] > out['tmax']
    flag(reversed_range, 'tmin_above_tmax:all_temperatures_set_missing')
    out.loc[reversed_range, ['tmin', 'tmax', 'tmean']] = np.nan
    bad_mean = (out['tmean'] < out['tmin']) | (out['tmean'] > out['tmax'])
    flag(bad_mean, 'tmean_outside_daily_range:set_missing')
    out.loc[bad_mean, 'tmean'] = np.nan
    for column in ['rain_mm', 'snowfall_cm', 'precip_mm']:
        bad = out[column] < 0
        flag(bad, f'{column}:negative:set_missing')
        out.loc[bad, column] = np.nan

    # Keep observed mean distinct from the optional calculated analysis mean.
    out['tmean_analysis'] = out['tmean']
    derive = (normalized['tmean'].str.lower().isin(MISSING)
              & out['tmin'].notna() & out['tmax'].notna())
    if not derive_mean:
        derive[:] = False
    out['tmean_derived'] = derive
    out.loc[derive, 'tmean_analysis'] = (out.loc[derive, 'tmin'] + out.loc[derive, 'tmax']) / 2
    flag(derive, 'tmean_analysis:derived_from_same_day_min_max')

    # Only truly identical source rows can be deduplicated automatically.
    repeated = normalized.duplicated(keep='first')
    candidates = ~repeated & ~invalid_date & station_ok
    conflicts = pd.Series(False, index=raw.index)
    conflicts.loc[candidates] = out.loc[candidates, 'date'].duplicated(keep=False)
    flag(repeated, 'identical_duplicate:removed')
    flag(conflicts, 'conflicting_date:all_candidates_quarantined')
    quarantine = (~candidates | conflicts) & ~repeated
    keep = ~repeated & ~quarantine
    out['quality_notes'] = notes.str.rstrip(';')
    month = out['date'].dt.month
    out['winter_year'] = (out['date'].dt.year + month.eq(12).astype(int)).where(
        month.isin(WINTER_MONTHS)).astype('Int64')

    review = raw.copy()
    review.insert(0, 'city', city)
    review.insert(1, 'source_file', path.name)
    review.insert(2, 'source_row', raw.index + 2)
    review['action'] = 'retained_with_annotation'
    review.loc[quarantine, 'action'] = 'quarantined'
    review.loc[repeated, 'action'] = 'identical_duplicate_removed'
    review['quality_notes'] = out['quality_notes']
    review = review.loc[notes.ne('')].copy()
    clean = out.loc[keep].sort_values('date').reset_index(drop=True)
    profile = {
        'city': city, 'input_rows': len(raw), 'clean_rows': len(clean),
        'identical_duplicates_removed': int(repeated.sum()),
        'quarantined_rows': int(quarantine.sum()), 'annotated_rows': len(review),
        'first_date': clean['date'].min(), 'last_date': clean['date'].max(),
        'derived_means': int(clean['tmean_derived'].sum()),
        **{f'missing_{c}': int(clean[c].isna().sum()) for c in NUMERIC},
        'missing_tmean_analysis': int(clean['tmean_analysis'].isna().sum()),
    }
    return clean, review, profile


def winter_reports(clean, city, first_year, last_year):
    dates = pd.date_range(f'{first_year-1}-12-01', f'{last_year}-03-01', inclusive='left')
    dates = dates[dates.month.isin(WINTER_MONTHS)]
    calendar = clean.set_index('date').reindex(dates)
    calendar.index.name = 'date'
    calendar['city'] = city
    calendar['winter_year'] = calendar.index.year + (calendar.index.month == 12).astype(int)
    calendar['record_present'] = calendar['source_row'].notna()
    absent = calendar.loc[~calendar['record_present'], ['city', 'winter_year']].reset_index()
    months = []
    for period, block in calendar.groupby(calendar.index.to_period('M')):
        valid = block['tmean_analysis'].count()
        missing = len(block) - valid
        run = longest_missing(block['tmean_analysis'])
        months.append({
            'city': city, 'month': str(period), 'winter_year': int(block['winter_year'].iloc[0]),
            'expected_days': len(block), 'recorded_days': int(block['record_present'].sum()),
            'valid_temperature_days': valid, 'missing_temperature_days': missing,
            'max_consecutive_missing_temperature': run,
            'temperature_pass': missing <= MAX_MONTHLY_MISSING and run <= MAX_CONSECUTIVE_MISSING,
            'valid_snowfall_days': block['snowfall_cm'].count(),
            'snowfall_complete': block['snowfall_cm'].notna().all(),
            'tmin_complete': block['tmin'].notna().all(),
        })
    monthly = pd.DataFrame(months)
    winters = []
    for year, block in calendar.groupby('winter_year'):
        checks = monthly.loc[monthly['winter_year'].eq(year)]
        temperature_pass = bool(checks['temperature_pass'].all())
        snowfall_pass = bool(checks['snowfall_complete'].all())
        tmin_pass = bool(checks['tmin_complete'].all())
        winters.append({
            'city': city, 'winter_year': year, 'expected_days': len(block),
            'recorded_days': int(block['record_present'].sum()),
            'missing_calendar_days': int((~block['record_present']).sum()),
            'valid_temperature_days': block['tmean_analysis'].count(),
            'valid_snowfall_days': block['snowfall_cm'].count(),
            'derived_temperature_days': int(block['tmean_derived'].eq(True).sum()),
            'temperature_pass': temperature_pass, 'snowfall_pass': snowfall_pass,
            'cold_days_pass': tmin_pass,
            'mean_temp': block['tmean_analysis'].mean() if temperature_pass else np.nan,
            'snowfall_total_cm': block['snowfall_cm'].sum() if snowfall_pass else np.nan,
            'snow_days': int(block['snowfall_cm'].ge(SNOW_DAY_CM).sum()) if snowfall_pass else np.nan,
            'days_below_m20': int(block['tmin'].le(COLD_DAY_C).sum()) if tmin_pass else np.nan,
            'exclusion_reasons': ';'.join(reason for passed, reason in [
                (temperature_pass, 'temperature:monthly_3_and_5_failed'),
                (snowfall_pass, 'snow_metrics:incomplete_daily_snowfall'),
                (tmin_pass, 'cold_days:incomplete_daily_tmin')] if not passed),
        })
    return monthly, pd.DataFrame(winters), absent
