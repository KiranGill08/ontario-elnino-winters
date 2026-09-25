"""Rebuild DJF index values from the bundled official NOAA HTML snapshots.

This uses published one-decimal table values, including exact threshold values.
The bundled snapshots are frozen; this script makes no network requests.
"""
from io import StringIO
from pathlib import Path
import hashlib
import json
import pandas as pd
import sys
# Let this script find config.py and the modules in the numbered subfolders.
_PY = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(_PY)] + sorted(str(p) for p in _PY.iterdir() if p.is_dir() and p.name[:2].isdigit())
import config as cfg

URLS = {
    'oni': 'https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/',
    'roni': 'https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/',
}


def extract(path, index):
    candidates = []
    for table in pd.read_html(StringIO(path.read_text(encoding='utf-8', errors='replace'))):
        if table.shape[1] != 13:
            continue
        numeric_year = table.iloc[:, 0].astype(str).str.fullmatch(r'\d{4}')
        if numeric_year.sum() >= 45:
            selected = table.loc[numeric_year].iloc[:, :2].copy()
            selected.columns = ['winter_year', f'{index}_djf']
            selected = selected.apply(pd.to_numeric, errors='raise')
            candidates.append((len(table), selected))
    if not candidates:
        raise ValueError(f'No NOAA year/DJF table found in {path}')
    result = min(candidates, key=lambda item: item[0])[1]
    if result['winter_year'].duplicated().any():
        raise ValueError('Duplicate years in index source')
    result['winter_year'] = result['winter_year'].astype(int)
    return result


def main():
    folder = cfg.ROOT / 'data' / 'external'
    tables = []
    sources = []
    for index in ['oni', 'roni']:
        path = folder / 'source_snapshots' / f'{index}_v6.html'
        tables.append(extract(path, index))
        sources.append({'index': index.upper(), 'url': URLS[index], 'version': 'ERSSTv6',
                        'retrieved_date': '2026-09-21', 'file': path.name,
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'values': 'Published one-decimal DJF table values'})
    combined = tables[0].merge(tables[1], on='winter_year', validate='one_to_one')
    combined = combined.loc[combined['winter_year'].between(cfg.FIRST_WINTER, cfg.LAST_WINTER)]
    if len(combined) != cfg.LAST_WINTER - cfg.FIRST_WINTER + 1 or combined.isna().any().any():
        raise ValueError('Missing study winters in NOAA snapshots')
    combined.to_csv(folder / 'enso_djf.csv', index=False)
    (folder / 'enso_sources.json').write_text(json.dumps(sources, indent=2), encoding='utf-8')
    print(combined.to_string(index=False))


if __name__ == '__main__':
    main()
