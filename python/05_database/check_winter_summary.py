"""Check that the SQL winter summary matches pandas (Definition of Done).

    python python/05_database/check_winter_summary.py                 # latest run
    python python/05_database/check_winter_summary.py --run runs/<timestamp>

Compares every row of result_winter_summary_sql (built by sql/winter_summary.sql)
with data/enso_group_summary.csv from the same pipeline run: winter counts and the
lists of eligible winters must be equal, and mean, median, standard deviation, min and
max must agree to the CSV's precision (the pipeline writes 10 significant digits).
"""
from pathlib import Path
import argparse
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from load_database import DEFAULT_DB, ROOT, latest_run
import sqlite3

KEY = ['city', 'enso_index', 'enso_group', 'metric']
COUNTS = ['n_group_winters', 'n_eligible']
STATS = ['mean', 'median', 'std', 'min', 'max']


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--run', type=Path, help='run folder the database was loaded from (default: latest)')
    parser.add_argument('--db', type=Path, default=DEFAULT_DB, help='database file (default: sql/ontario_enso.db)')
    args = parser.parse_args(argv)
    run = (args.run if args.run.is_absolute() else ROOT / args.run) if args.run else latest_run()
    pandas_table = pd.read_csv(run / 'data' / 'enso_group_summary.csv')

    if not args.db.is_file():
        raise SystemExit(f'{args.db} not found. Run python python/05_database/load_database.py first.')
    connection = sqlite3.connect(args.db)
    try:
        loaded = connection.execute('SELECT run_folder FROM meta_pipeline_runs').fetchone()[0]
        rows = connection.execute(f"SELECT {', '.join(KEY + COUNTS + STATS)}, eligible_years "
                                  'FROM result_winter_summary_sql').fetchall()
        sql_table = pd.DataFrame(rows, columns=KEY + COUNTS + STATS + ['eligible_years'])
    finally:
        connection.close()
    if loaded != run.name:
        print(f'Note: the database holds run {loaded}, but you are checking against {run.name}.')

    sql_table[STATS] = sql_table[STATS].astype(float)
    merged = pandas_table.merge(sql_table, on=KEY, how='outer', suffixes=('_pandas', '_sql'), indicator=True)
    problems = []
    unmatched = merged.loc[merged['_merge'] != 'both']
    if len(unmatched):
        problems.append(f'{len(unmatched)} rows exist on only one side:\n{unmatched[KEY + ["_merge"]].to_string(index=False)}')
    both = merged.loc[merged['_merge'] == 'both']
    for column in COUNTS:
        bad = both.loc[both[f'{column}_pandas'] != both[f'{column}_sql']]
        if len(bad):
            problems.append(f'{column}: {len(bad)} rows differ')
    for column in STATS:
        a, b = both[f'{column}_pandas'].to_numpy(float), both[f'{column}_sql'].to_numpy(float)
        bad = ~(np.isclose(a, b, rtol=1e-8, atol=1e-9) | (np.isnan(a) & np.isnan(b)))
        if bad.any():
            problems.append(f'{column}: {bad.sum()} rows differ (largest gap {np.nanmax(np.abs(a - b)):.3g})')
    years = both['eligible_years_pandas'].fillna('').astype(str) != both['eligible_years_sql'].fillna('').astype(str)
    if years.any():
        problems.append(f'eligible_years: {years.sum()} rows differ')

    if problems:
        print('SQL and pandas winter summaries DO NOT match:')
        print('\n'.join(f'  - {p}' for p in problems))
        return 1
    print(f'SQL winter summary matches pandas: {len(both)} rows '
          f'({both["city"].nunique()} cities x 2 indices x 4 ENSO groups x {both["metric"].nunique()} KPIs), '
          'counts and winters equal, statistics equal to 10 significant digits.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
