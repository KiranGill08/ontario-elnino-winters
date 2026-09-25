"""Read, clean and quality-screen the original CSVs without overwriting them."""
import csv
import numpy as np
import pandas as pd
import sys
from pathlib import Path
# Let this script find config.py and the modules in the numbered subfolders.
_PY = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(_PY)] + sorted(str(p) for p in _PY.iterdir() if p.is_dir() and p.name[:2].isdigit())
from config import (COLUMNS, NUMERIC, MISSING, TEMPERATURE_SCREEN_C,
                    MAX_MONTHLY_MISSING, MAX_CONSECUTIVE_MISSING,
                    SNOW_DAY_CM, COLD_DAY_C, WINTER_MONTHS)

# Statistics Canada symbols meaning "not available" or "suppressed" in this table
# (distinct from 'E', which means the value IS present but should be used with caution).
MAPLE_MISSING = {'..', 'f', 'x', ''}
GDP_MISSING = {'..', 'f', 'x', ''}


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


def spring_reports(clean, city, first_year, last_year, months=(2, 3, 4)):
    """Same monthly 3-and-5 quality screening as winter_reports(), but for the
    maple sap season (default: February-April) instead of December-February.

    Unlike a winter, this window falls entirely inside one calendar year, so
    there's no December wraparound to handle -- `year` here is a plain calendar
    year, the same "year" StatCan's maple production table uses, so the two can
    be merged directly with no shift.

    Adds `freeze_thaw_days` (tmin < 0C and tmax > 0C on the same day) alongside
    the usual metrics, since alternating freeze/thaw is the specific mechanism
    that drives maple sap flow -- a plain cold-days count doesn't capture that.
    """
    def season_days(year):
        start = pd.Timestamp(year=year, month=months[0], day=1)
        end = pd.Timestamp(year=year, month=months[-1], day=1) + pd.offsets.MonthEnd(0)
        return pd.date_range(start, end, freq='D')

    dates = pd.DatetimeIndex(np.concatenate(
        [season_days(year) for year in range(first_year, last_year + 1)]))

    calendar = clean.set_index('date').reindex(dates)
    calendar.index.name = 'date'
    calendar['city'] = city
    calendar['season_year'] = calendar.index.year
    calendar['record_present'] = calendar['source_row'].notna()
    absent = calendar.loc[~calendar['record_present'], ['city', 'season_year']].reset_index()

    month_rows = []
    for period, block in calendar.groupby(calendar.index.to_period('M')):
        valid = block['tmean_analysis'].count()
        missing = len(block) - valid
        run = longest_missing(block['tmean_analysis'])
        month_rows.append({
            'city': city, 'month': str(period), 'season_year': int(block['season_year'].iloc[0]),
            'expected_days': len(block), 'recorded_days': int(block['record_present'].sum()),
            'valid_temperature_days': valid, 'missing_temperature_days': missing,
            'max_consecutive_missing_temperature': run,
            'temperature_pass': missing <= MAX_MONTHLY_MISSING and run <= MAX_CONSECUTIVE_MISSING,
            'valid_snowfall_days': block['snowfall_cm'].count(),
            'snowfall_complete': block['snowfall_cm'].notna().all(),
            'tmin_complete': block['tmin'].notna().all(),
            'tmax_complete': block['tmax'].notna().all(),
        })
    monthly = pd.DataFrame(month_rows)

    seasons = []
    for year, block in calendar.groupby('season_year'):
        checks = monthly.loc[monthly['season_year'].eq(year)]
        temperature_pass = bool(checks['temperature_pass'].all())
        snowfall_pass = bool(checks['snowfall_complete'].all())
        tmin_pass = bool(checks['tmin_complete'].all())
        freeze_thaw_pass = tmin_pass and bool(checks['tmax_complete'].all())
        freeze_thaw = block['tmin'].lt(0) & block['tmax'].gt(0)
        seasons.append({
            'city': city, 'year': year, 'expected_days': len(block),
            'recorded_days': int(block['record_present'].sum()),
            'missing_calendar_days': int((~block['record_present']).sum()),
            'valid_temperature_days': block['tmean_analysis'].count(),
            'temperature_pass': temperature_pass, 'snowfall_pass': snowfall_pass,
            'cold_days_pass': tmin_pass, 'freeze_thaw_pass': freeze_thaw_pass,
            'mean_temp': block['tmean_analysis'].mean() if temperature_pass else np.nan,
            'snowfall_total_cm': block['snowfall_cm'].sum() if snowfall_pass else np.nan,
            'snow_days': int(block['snowfall_cm'].ge(SNOW_DAY_CM).sum()) if snowfall_pass else np.nan,
            'days_below_m20': int(block['tmin'].le(COLD_DAY_C).sum()) if tmin_pass else np.nan,
            'freeze_thaw_days': int(freeze_thaw.sum()) if freeze_thaw_pass else np.nan,
        })
    return monthly, pd.DataFrame(seasons), absent


def clean_maple_syrup(path):
    """Read a Statistics Canada "Production and value of maple products" CSV
    (table 32-10-0354-01, one province per file, wide by year) and return a tidy
    one-row-per-year table plus a profile dict. Not yet wired into run_pipeline.py --
    call this directly, the same way the other standalone scripts are run.

    Note on joining to the rest of this project: StatCan's "year" here is a
    calendar year, and the maple season it reports (roughly February-April) falls
    in the same calendar year as this project's `winter_year` (the year in which
    February falls) for the same winter. So a direct `year == winter_year` merge
    with enso_djf.csv or winter_kpis.csv lines the two up correctly with no shift.
    """
    # StatCan's export is a ragged CSV (metadata lines have 1 field, data lines have
    # many), which pandas' own CSV reader rejects -- read it row by row instead and
    # pad every row out to the widest row so it still lines up in a DataFrame.
    with open(path, encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.reader(handle))
    if not rows:
        raise ValueError(f'{path.name}: file has no rows')
    width = max(len(row) for row in rows)
    rows = [row + [''] * (width - len(row)) for row in rows]
    raw = pd.DataFrame(rows, dtype='string').fillna('')

    header_rows = raw.index[raw[0].str.startswith('Maple products', na=False)]
    if header_rows.empty:
        raise ValueError(f'{path.name}: could not find the "Maple products" header row')
    header_row = header_rows[0]

    year_numbers = pd.to_numeric(raw.loc[header_row], errors='coerce')
    year_columns = year_numbers.index[year_numbers.notna() & (raw.columns != 0)]
    if year_columns.empty:
        raise ValueError(f'{path.name}: no year columns found in the header row')
    years = year_numbers.loc[year_columns].astype(int)

    def find_row(label_prefix):
        matches = raw.index[raw[0].str.startswith(label_prefix, na=False)]
        if matches.empty:
            raise ValueError(f'{path.name}: could not find a row starting with {label_prefix!r}')
        return matches[0]

    def extract(label_prefix):
        row = raw.loc[find_row(label_prefix), year_columns]
        flagged = row.str.contains('E', regex=False, na=False)
        stripped = row.str.replace(',', '', regex=False).str.rstrip('E')
        missing = stripped.str.strip().str.lower().isin(MAPLE_MISSING)
        values = pd.to_numeric(stripped.mask(missing), errors='coerce')
        return values.to_numpy(), flagged.to_numpy(), missing.to_numpy()

    syrup_values, syrup_flagged, syrup_missing = extract('Maple products expressed as syrup')
    value_values, value_flagged, value_missing = extract('Gross value of maple products')

    clean = pd.DataFrame({
        'year': years.to_numpy(),
        'syrup_thousand_gallons': syrup_values,
        'gross_value_thousand_cad': value_values,
    }).sort_values('year').reset_index(drop=True)
    # Re-align the flag arrays to the same sort order as `clean`.
    order = years.to_numpy().argsort()
    syrup_flagged, value_flagged = syrup_flagged[order], value_flagged[order]
    syrup_missing, value_missing = syrup_missing[order], value_missing[order]

    notes = pd.Series('', index=clean.index, dtype='string')

    def flag(mask, message):
        mask = pd.Series(mask, index=clean.index).fillna(False)
        notes.loc[mask] = notes.loc[mask] + message + ';'

    flag(syrup_flagged, 'syrup_thousand_gallons:use_with_caution')
    flag(value_flagged, 'gross_value_thousand_cad:use_with_caution')
    flag(syrup_missing, 'syrup_thousand_gallons:not_available:set_missing')
    flag(value_missing, 'gross_value_thousand_cad:not_available:set_missing')
    # StatCan footnote: from 1986 on, Ontario's survey is weighted by spring tap counts;
    # earlier years used a different (unweighted) survey method, so trend comparisons
    # spanning 1986 should treat it as a methodology break, not a real jump in production.
    flag(clean['year'].lt(1986), 'pre_1986:survey_not_tap_weighted:methodology_break_at_1986')

    clean['quality_notes'] = notes.str.rstrip(';')
    profile = {
        'input_years': len(clean),
        'first_year': int(clean['year'].min()), 'last_year': int(clean['year'].max()),
        'use_with_caution_years': int((syrup_flagged | value_flagged).sum()),
        'missing_syrup_years': int(clean['syrup_thousand_gallons'].isna().sum()),
        'missing_value_years': int(clean['gross_value_thousand_cad'].isna().sum()),
        'pre_1986_years': int(clean['year'].lt(1986).sum()),
    }
    return clean, profile


def clean_gdp(path, geography='Ontario'):
    """Read a Statistics Canada "Gross domestic product, expenditure-based,
    provincial and territorial, annual" CSV (table 36-10-0222-01, multiple
    geographies side by side, wide by year) and return a tidy one-row-per-year
    table for a single geography, plus a profile dict.

    Note on joining to the rest of this project: StatCan's "year" here is a
    calendar year. This project treats a calendar year's economic activity as
    co-occurring with the winter labelled the same year (Dec of year-1 through
    Feb of that year is winter_year == that year) -- the same convention already
    used for maple syrup and the sap-season analysis. A direct `year ==
    winter_year` merge with enso_djf.csv or winter_kpis.csv lines the two up
    with no shift.
    """
    # Same ragged-CSV shape as the maple syrup export: metadata lines have 1
    # field, data lines have many (here, one column per year per geography).
    with open(path, encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.reader(handle))
    if not rows:
        raise ValueError(f'{path.name}: file has no rows')
    width = max(len(row) for row in rows)
    rows = [row + [''] * (width - len(row)) for row in rows]
    raw = pd.DataFrame(rows, dtype='string').fillna('')

    def find_row_exact(label):
        matches = raw.index[raw[0].eq(label)]
        if matches.empty:
            raise ValueError(f'{path.name}: could not find a row equal to {label!r}')
        return matches[0]

    def find_row(label_prefix):
        matches = raw.index[raw[0].str.startswith(label_prefix, na=False)]
        if matches.empty:
            raise ValueError(f'{path.name}: could not find a row starting with {label_prefix!r}')
        return matches[0]

    # Exact match for the "Geography" header row -- the file's own metadata
    # preamble includes a line like "Geography: Canada, Province or territory"
    # that would otherwise match a startswith search.
    geo_row = raw.loc[find_row_exact('Geography')]
    year_row = raw.loc[find_row_exact('Estimates')]
    gdp_row = raw.loc[find_row('Gross domestic product at market prices')]

    # Each geography gets its own block of year-columns; a block starts wherever
    # the geography row has a non-blank label (StatCan doesn't repeat the label
    # across every column in the block).
    block_starts = [j for j in raw.columns[1:] if geo_row[j].strip()]
    if not block_starts:
        raise ValueError(f'{path.name}: no geography columns found')
    block_bounds = block_starts + [width]

    target = None
    for k in range(len(block_starts)):
        start, end = block_bounds[k], block_bounds[k + 1]
        label = geo_row[start].strip()
        # StatCan appends a footnote marker to some labels (e.g. "Canada 1").
        if label == geography or label.startswith(geography + ' '):
            target = (start, end)
            break
    if target is None:
        found = [geo_row[j].strip() for j in block_starts]
        raise ValueError(f'{path.name}: geography {geography!r} not found; available: {found}')
    start, end = target

    years = pd.to_numeric(year_row.loc[start:end - 1], errors='coerce')
    year_columns = years.index[years.notna()]
    years = years.loc[year_columns].astype(int)

    values_raw = gdp_row.loc[year_columns]
    stripped = values_raw.str.replace(',', '', regex=False).str.rstrip('E')
    flagged = values_raw.str.contains('E', regex=False, na=False)
    missing = stripped.str.strip().str.lower().isin(GDP_MISSING)
    values = pd.to_numeric(stripped.mask(missing), errors='coerce')

    clean = pd.DataFrame({
        'year': years.to_numpy(),
        'gdp_chained_2017_millions': values.to_numpy(),
    }).sort_values('year').reset_index(drop=True)
    order = years.to_numpy().argsort()
    flagged, missing = flagged.to_numpy()[order], missing.to_numpy()[order]

    clean['gdp_growth_pct'] = clean['gdp_chained_2017_millions'].pct_change() * 100

    notes = pd.Series('', index=clean.index, dtype='string')

    def flag(mask, message):
        mask = pd.Series(mask, index=clean.index).fillna(False)
        notes.loc[mask] = notes.loc[mask] + message + ';'

    flag(flagged, 'gdp_chained_2017_millions:use_with_caution')
    flag(missing, 'gdp_chained_2017_millions:not_available:set_missing')
    clean['quality_notes'] = notes.str.rstrip(';')

    profile = {
        'geography': geography,
        'input_years': len(clean),
        'first_year': int(clean['year'].min()), 'last_year': int(clean['year'].max()),
        'use_with_caution_years': int(flagged.sum()),
        'missing_years': int(clean['gdp_chained_2017_millions'].isna().sum()),
    }
    return clean, profile


if __name__ == '__main__':
    # Running this file directly cleans the maple syrup and Ontario GDP data and
    # writes both to data/processed/, overwriting whatever was there before.
    # This is the one place clean_data.py knows about an output path --
    # everything above this line stays a pure function with no file writing of
    # its own; run_pipeline.py is still what produces every other file in
    # data/processed/.
    import config as cfg
    from calculate_kpis import load_enso

    if not cfg.MAPLE_SYRUP_FILE.is_file():
        raise SystemExit(f'No file at {cfg.MAPLE_SYRUP_FILE}')
    maple, maple_profile = clean_maple_syrup(cfg.MAPLE_SYRUP_FILE)
    enso = load_enso(cfg.ENSO_FILE)
    maple = maple.merge(enso[['winter_year', 'enso_class_oni', 'enso_class_roni']],
                         left_on='year', right_on='winter_year', how='left').drop(columns='winter_year')

    out_path = cfg.ROOT / 'data' / 'processed' / 'ontario_maple_syrup_production.csv'
    maple.to_csv(out_path, index=False, float_format='%.10g')
    print(f"Wrote {out_path}")
    print(f"  years: {maple_profile['first_year']}-{maple_profile['last_year']} ({maple_profile['input_years']} rows)")
    print(f"  flagged use-with-caution: {maple_profile['use_with_caution_years']}")
    print(f"  pre-1986 (methodology break): {maple_profile['pre_1986_years']}")

    if cfg.GDP_FILE.is_file():
        gdp, gdp_profile = clean_gdp(cfg.GDP_FILE, geography='Ontario')
        gdp = gdp.merge(enso[['winter_year', 'enso_class_oni', 'enso_class_roni']],
                         left_on='year', right_on='winter_year', how='left').drop(columns='winter_year')
        gdp_out_path = cfg.ROOT / 'data' / 'processed' / 'ontario_gdp.csv'
        gdp.to_csv(gdp_out_path, index=False, float_format='%.10g')
        print(f"Wrote {gdp_out_path}")
        print(f"  years: {gdp_profile['first_year']}-{gdp_profile['last_year']} ({gdp_profile['input_years']} rows)")
    else:
        print(f'Skipping GDP: no file at {cfg.GDP_FILE}')
