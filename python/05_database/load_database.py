"""Load one pipeline run into the SQLite database sql/ontario_enso.db.

    python python/05_database/load_database.py                 # latest run in runs/
    python python/05_database/load_database.py --run runs/20260925_214558
    python python/05_database/load_database.py --db path/to/other.db

Steps: rebuild every table from sql/schema.sql, load the run's CSVs, build the
winter summary in SQL (sql/winter_summary.sql), create the dashboard views
(sql/dashboard_views.sql), then record the load in meta_pipeline_runs. Every load replaces the previous one, so the database always
matches exactly one run. Uses Python's built-in sqlite3: nothing to install.
"""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import math
import sqlite3
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_FILE = ROOT / 'sql' / 'schema.sql'
SUMMARY_FILE = ROOT / 'sql' / 'winter_summary.sql'
DASHBOARD_FILE = ROOT / 'sql' / 'dashboard_views.sql'
DEFAULT_DB = ROOT / 'sql' / 'ontario_enso.db'
AUTO_KEYS = {'row_id', 'run_id'}   # filled by SQLite, not by the CSVs

CITY_INFO = ['city_name', 'region', 'latitude_approx', 'included_in_proposal', 'included_in_repo_study']
ENSO_LABELS = ['oni_djf', 'roni_djf', 'enso_class_oni', 'strong_el_nino_oni', 'enso_class_roni',
               'strong_el_nino_roni', 'enso_index', 'enso_value', 'enso_class', 'strong_el_nino']
WINTER_FIELDS = ['mean_temp', 'temp_anomaly', 'snowfall_total_cm', 'snow_days', 'days_below_m20',
                 'baseline_mean_temp', 'baseline_n_winters', 'baseline_status', 'winter_label',
                 'temperature_pass', 'snowfall_pass', 'cold_days_pass']


# (table, file inside the run folder, columns to drop, optional custom reader)
# Columns kept must match sql/schema.sql exactly; the loader checks this.
TABLES = [
    # lookups
    ('dim_city', 'data/city_baselines.csv', None, lambda p: pd.read_csv(p)[['city'] + CITY_INFO]),
    ('dim_enso_winter', 'data/enso_winter_labels.csv', [], None),
    # measured data
    ('fact_daily_weather', 'data/all_stations_daily_enriched.csv', CITY_INFO + ENSO_LABELS + WINTER_FIELDS, None),
    ('fact_winter_kpis', 'data/winter_kpis.csv', CITY_INFO + ENSO_LABELS, None),
    ('fact_sap_season', 'data/sap_season_kpis.csv', [], None),
    ('fact_growing_season', 'data/growing_season_kpis.csv', ['enso_class_oni', 'enso_class_roni'], None),
    ('fact_maple_production', 'data/ontario_maple_syrup_production.csv', ['enso_class_oni', 'enso_class_roni'], None),
    ('fact_ontario_gdp', 'data/ontario_gdp.csv', ['enso_class_oni', 'enso_class_roni'], None),
    # results (result_winter_summary_sql is built in SQL afterwards)
    ('result_city_baselines', 'data/city_baselines.csv', CITY_INFO, None),
    ('result_temperature_trends', 'data/temperature_trends.csv', [], None),
    ('result_enso_comparisons', 'data/enso_comparisons.csv', CITY_INFO, None),
    ('result_trend_sensitivity', 'data/temperature_trend_sensitivity.csv', CITY_INFO, None),
    ('result_regional_comparisons', 'data/regional_comparisons.csv', [], None),
    ('result_heating_demand', 'data/chart_data/eda_heating_demand_by_city.csv', [], None),
    ('result_growing_season', 'data/chart_data/eda_growing_season_by_city.csv', [], None),
    ('result_maple_freeze_thaw', 'data/chart_data/eda_freeze_thaw_vs_maple.csv', [], None),
    ('result_impact_tests', 'data/chart_impact_tests.csv', [], None),
    ('result_index_slopes', 'data/chart_index_vs_anomaly_slopes.csv', [], None),
]


def latest_run():
    runs = sorted(p for p in (ROOT / 'runs').glob('*') if (p / 'run_manifest.json').is_file())
    if not runs:
        raise SystemExit('No finished run in runs/. Run python python/run_pipeline.py first.')
    return runs[-1]


def connect(db_path):
    connection = sqlite3.connect(db_path)
    connection.execute('PRAGMA foreign_keys = ON')
    try:
        connection.execute('SELECT sqrt(4)')
    except sqlite3.OperationalError:          # some SQLite builds lack math functions
        connection.create_function('sqrt', 1, lambda x: None if x is None else math.sqrt(x), deterministic=True)
    return connection


def table_columns(connection, table):
    return [row[1] for row in connection.execute(f'PRAGMA table_info("{table}")') if row[1] not in AUTO_KEYS]


def to_sqlite_value(value):
    """NaN/blank -> NULL, numpy numbers -> Python numbers, True/False -> 1/0."""
    if value is None or (isinstance(value, float) and np.isnan(value)) or value is pd.NA or value is pd.NaT:
        return None
    if isinstance(value, (bool, np.bool_)):
        return int(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if text in ('True', 'False'):
            return int(text == 'True')
        return text or None
    return value


def load_table(connection, run, table, source, drop, reader):
    path = run / source
    if not path.is_file():
        raise SystemExit(f'{table}: missing {path}')
    frame = reader(path) if reader else pd.read_csv(path, low_memory=False)
    if drop:
        frame = frame.drop(columns=[c for c in drop if c in frame.columns])
    columns = table_columns(connection, table)
    if not columns:
        raise SystemExit(f'{table}: not in sql/schema.sql')
    missing, extra = set(columns) - set(frame.columns), set(frame.columns) - set(columns)
    if missing or extra:
        raise SystemExit(f'{table}: columns differ from sql/schema.sql. '
                         f'In schema only: {sorted(missing)}. In CSV only: {sorted(extra)}')
    rows = [tuple(to_sqlite_value(v) for v in row) for row in frame[columns].itertuples(index=False)]
    connection.executemany(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['?'] * len(columns))})", rows)
    return len(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--run', type=Path, help='run folder to load (default: latest in runs/)')
    parser.add_argument('--db', type=Path, default=DEFAULT_DB, help='database file (default: sql/ontario_enso.db)')
    args = parser.parse_args(argv)
    run = (args.run if args.run.is_absolute() else ROOT / args.run) if args.run else latest_run()
    manifest = json.loads((run / 'run_manifest.json').read_text(encoding='utf-8'))

    connection = connect(args.db)
    try:
        connection.executescript(SCHEMA_FILE.read_text(encoding='utf-8'))
        print(f'Loading {run.name} into {args.db}')
        total = 0
        specs = TABLES
        with connection:                      # one transaction: all tables load, or none
            for spec in specs:
                n = load_table(connection, run, *spec)
                total += n
                print(f'  {spec[0]:40s} {n:7,d} rows')
            connection.executescript(SUMMARY_FILE.read_text(encoding='utf-8'))
            connection.executescript(DASHBOARD_FILE.read_text(encoding='utf-8'))
            connection.execute('INSERT INTO meta_pipeline_runs (run_folder, pipeline_completed_utc, loaded_utc, '
                               'validation, daily_rows, winter_rows, manifest_json) VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (run.name, manifest['completed_utc'][:19].replace('T', ' '),
                                datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'), manifest['validation'],
                                manifest['daily_rows'], manifest['winter_rows'], json.dumps(manifest)))
        bad = connection.execute('PRAGMA foreign_key_check').fetchall()
        if bad:
            raise SystemExit(f'Foreign-key problems: {bad[:5]}')
        connection.execute('VACUUM')
    finally:
        connection.close()
    size_mb = args.db.stat().st_size / 1e6
    print(f'Loaded {total:,} rows into {len(specs)} tables, plus the SQL winter summary, dashboard views and run record. '
          f'{args.db.name}: {size_mb:.1f} MB')


if __name__ == '__main__':
    sys.exit(main())
