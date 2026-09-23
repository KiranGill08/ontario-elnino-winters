"""Edit shared project settings here, then rerun run_pipeline.py."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / 'data' / 'interim'
ENSO_FILE = ROOT / 'data' / 'external' / 'enso_djf.csv'
# Province-level, annual, not per-station -- see the note in run_pipeline.py on why
# this is written out as its own CSV rather than merged into the winters table.
MAPLE_SYRUP_FILE = ROOT / 'data' / 'raw' / 'maple-production.csv'
# Same rationale: province-level, annual, not per-station.
GDP_FILE = ROOT / 'data' / 'raw'  / 'ontario-gdp.csv'
STATIONS = ['london', 'ottawa', 'sudbury', 'thunderbay', 'toronto', 'windsor']
PRIMARY_STATIONS = ['windsor', 'toronto', 'ottawa', 'thunderbay']
REPO_STATIONS = ['windsor', 'toronto', 'ottawa', 'sudbury', 'thunderbay']
CITY_NAMES = dict(london='London', ottawa='Ottawa', sudbury='Sudbury',
                  thunderbay='Thunder Bay', toronto='Toronto Pearson', windsor='Windsor')
LATITUDES = dict(london=43.03, ottawa=45.32, sudbury=46.63,
                 thunderbay=48.37, toronto=43.68, windsor=42.28)
REGIONS = dict(london='Southwest', ottawa='East', sudbury='Northeast',
               thunderbay='Northwest', toronto='South-central', windsor='Southwest')
FIRST_WINTER = 1982  # December 1981 to February 1982
LAST_WINTER = 2026
BASELINE_START = 1991  # First baseline winter begins December 1990
BASELINE_END = 2020
WINTER_MONTHS = [12, 1, 2]
PRIMARY_INDEX = 'RONI'  # Both ONI and RONI comparisons are always saved
EL_NINO_THRESHOLD = 0.5
LA_NINA_THRESHOLD = -0.5
STRONG_THRESHOLD = 1.5
TEMPERATURE_SCREEN_C = (-50, 45)
MAX_MONTHLY_MISSING = 5
MAX_CONSECUTIVE_MISSING = 3
DERIVE_MISSING_MEAN = True
SNOW_DAY_CM = 1.0
COLD_DAY_C = -20.0
BOOTSTRAP_SAMPLES = 10000
RANDOM_SEED = 20260921
QUALITY_METHOD = 'monthly_3_and_5_temperature_complete_snow_and_tmin'
NUMERIC = ['tmax', 'tmin', 'tmean', 'rain_mm', 'snowfall_cm', 'precip_mm']
COLUMNS = ['date', *NUMERIC, 'station_id']
MISSING = {'', 'm', 'na', 'n/a', 'nan', 'none', 'null', '-9999.9'}
METRICS = {
    'mean_temp': ('Mean winter temperature', 'degrees C'),
    'temp_anomaly': ('Winter temperature anomaly', 'degrees C'),
    'snowfall_total_cm': ('Total winter snowfall', 'cm'),
    'snow_days': ('Snow days', 'days'),
    'days_below_m20': ('Very cold days', 'days'),
}
CLASS_ORDER = ['La Nina', 'Neutral', 'El Nino']


def validate():
    if PRIMARY_INDEX not in ['ONI', 'RONI']:
        raise ValueError('PRIMARY_INDEX must be ONI or RONI')
    if not FIRST_WINTER <= BASELINE_START <= BASELINE_END <= LAST_WINTER:
        raise ValueError('Baseline years must lie within the study years')
    if not LA_NINA_THRESHOLD < EL_NINO_THRESHOLD <= STRONG_THRESHOLD:
        raise ValueError('ENSO thresholds are inconsistent')
    if not set(PRIMARY_STATIONS).issubset(STATIONS):
        raise ValueError('Primary stations must be included in STATIONS')