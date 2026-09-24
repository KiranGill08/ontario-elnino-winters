"""
download_station.py

Downloads daily climate data for one station from Environment and Climate
Change Canada (ECCC) and combines records that are split across several
station IDs into one daily table.

Usage (run from your project root):
    pip install requests pandas
    python download_station.py NAME ID [ID ...] [--start 1981] [--end 2026]

List the station IDs from NEWEST to OLDEST. Where two stations report the same
day, the earlier ID in your list wins.

Example for Windsor A (newer entry first, older entry second):
    python download_station.py windsor 54738 4716

Output:
    data/raw/NAME/NAME_ID_YEAR.csv     one raw file per station ID and year
    data/interim/NAME_daily.csv      combined daily table
"""

import argparse
import pathlib
import time

import pandas as pd
import requests

URL = (
    "https://climate.weather.gc.ca/climate_data/bulk_data_e.html"
    "?format=csv&stationID={sid}&Year={yr}&Month=1&Day=1"
    "&timeframe=2&submit=Download+Data"
)
HEADERS = {"User-Agent": "ontario-elnino-student-project (python-requests)"}

# Output name -> start of the ECCC column name (flag columns are ignored)
COLUMN_PREFIXES = {
    "date": "Date/Time",
    "tmax": "Max Temp",
    "tmin": "Min Temp",
    "tmean": "Mean Temp",
    "rain_mm": "Total Rain",
    "snowfall_cm": "Total Snow",
    "precip_mm": "Total Precip",
}
VALUE_COLUMNS = ["tmax", "tmin", "tmean", "rain_mm", "snowfall_cm", "precip_mm"]


def check_connection(ids, start):
    """Fetch one sample file and show exactly what the server returns."""
    sid = ids[-1]                      # oldest station, most likely to have 1990s data
    test_year = min(start + 14, 2020)  # 1995 when start is 1981
    url = URL.format(sid=sid, yr=test_year)
    print(f"Test request: station {sid}, year {test_year}")
    print(url)
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
    except requests.RequestException as err:
        print(f"Request failed: {err}")
        print("This is a connection problem (network, firewall, or VPN), "
              "not a data problem.\n")
        return False

    print(f"Status: {r.status_code}, size: {len(r.content)} bytes, "
          f"type: {r.headers.get('Content-Type')}")
    print("First 300 characters returned:")
    print(r.text[:300])
    print()
    if b"<html" in r.content[:300].lower():
        print("The server returned a web page instead of a CSV. "
              "Open the URL above in your browser to see what it says.\n")
        return False
    return True


def download_all(ids, start, end, raw_dir, name, pause):
    """Download one file per station ID per year. Existing files are skipped."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    for sid in ids:
        print(f"Station {sid}")
        for yr in range(start, end + 1):
            path = raw_dir / f"{name}_{sid}_{yr}.csv"
            if path.exists():
                continue
            try:
                r = requests.get(URL.format(sid=sid, yr=yr),
                                 headers=HEADERS, timeout=30)
            except requests.RequestException as err:
                print(f"  {yr}: request failed ({err})")
                continue

            looks_like_html = b"<html" in r.content[:300].lower()
            if not r.ok or len(r.content) < 200 or looks_like_html:
                print(f"  {yr}: no usable file returned (status {r.status_code})")
            else:
                path.write_bytes(r.content)   # empty years are saved too, so
                                              # reruns do not fetch them again
            time.sleep(pause)


def read_one(path, station_id):
    """Read one ECCC file and return a tidy dataframe (possibly empty)."""
    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="latin-1")

    tidy = pd.DataFrame()
    for out_name, prefix in COLUMN_PREFIXES.items():
        match = [c for c in df.columns if c.startswith(prefix) and "Flag" not in c]
        tidy[out_name] = df[match[0]] if match else pd.NA

    tidy["date"] = pd.to_datetime(tidy["date"], errors="coerce")
    for col in VALUE_COLUMNS:
        tidy[col] = pd.to_numeric(tidy[col], errors="coerce")

    tidy = tidy.dropna(subset=["date"])
    tidy = tidy.dropna(subset=VALUE_COLUMNS, how="all")   # keep rows with data
    tidy["station_id"] = station_id
    return tidy


def combine(ids, raw_dir, name, out_file):
    """Combine all downloaded files into one daily table."""
    frames = []
    for priority, sid in enumerate(ids):
        for path in sorted(raw_dir.glob(f"{name}_{sid}_*.csv")):
            df = read_one(path, sid)
            if not df.empty:
                df["priority"] = priority
                frames.append(df)

    if not frames:
        raise SystemExit("No data found. Check the station IDs and downloads.")

    data = pd.concat(frames, ignore_index=True)
    data = data.sort_values(["date", "priority"])
    data = data.drop_duplicates(subset="date", keep="first")   # keep newer ID
    data = data.sort_values("date").drop(columns="priority").reset_index(drop=True)

    out_file.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(out_file, index=False)
    return data


def report(data, start, end, out_file):
    """Print a summary so you can spot problems quickly."""
    print("\n=== Summary ===")
    print(f"Saved {len(data):,} daily rows to {out_file}")
    print(f"Date range: {data['date'].min().date()} to {data['date'].max().date()}")

    print("\nRows and date range per station ID:")
    by_station = data.groupby("station_id")["date"].agg(["count", "min", "max"])
    print(by_station.to_string())

    # Winter check: how many Dec-Feb days have a mean temperature, per winter
    d = data.dropna(subset=["tmean"]).copy()
    d = d[d["date"].dt.month.isin([12, 1, 2])]
    d["winter_year"] = d["date"].dt.year + (d["date"].dt.month == 12).astype(int)
    winter_days = d.groupby("winter_year").size()
    all_winters = pd.Index(range(start + 1, end + 1))
    winter_days = winter_days.reindex(all_winters, fill_value=0)

    passing = (winter_days >= 85).sum()
    print(f"\nWinters with at least 85 days of mean temperature "
          f"(out of about 90): {passing} of {len(winter_days)}")
    weak = winter_days[winter_days < 85]
    if weak.empty:
        print("All winters pass the 85 day rule.")
    else:
        print("Winters below 85 days (these would be dropped):")
        for wy, n in weak.items():
            print(f"  winter {wy - 1}-{str(wy)[-2:]}: {n} days")

    snow_days = data.dropna(subset=["snowfall_cm"]).shape[0]
    print(f"\nRows with a snowfall value: {snow_days:,}. "
          "If this is 0 or very small, this station may not report snowfall.")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("name", help="short name, for example windsor")
    parser.add_argument("ids", nargs="+", type=int,
                        help="station IDs, newest first")
    parser.add_argument("--start", type=int, default=1981)
    parser.add_argument("--end", type=int, default=2026)
    parser.add_argument("--pause", type=float, default=1.0,
                        help="seconds to wait between requests")
    args = parser.parse_args()

    raw_dir = pathlib.Path("data/raw") / args.name
    out_file = pathlib.Path("data/interim") / f"{args.name}_daily.csv"

    if not check_connection(args.ids, args.start):
        raise SystemExit("Stopping: fix the problem shown above, then run again.")

    download_all(args.ids, args.start, args.end, raw_dir, args.name, args.pause)
    data = combine(args.ids, raw_dir, args.name, out_file)
    report(data, args.start, args.end, out_file)


if __name__ == "__main__":
    main()