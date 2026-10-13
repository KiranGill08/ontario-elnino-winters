'''
Feature construction shared by the training script and the server.

Both must build a row the same way, or the model is served inputs that differ
from the ones it was trained on. Keeping the logic in one place is the point.
The rules here match notebooks/05_feature_engineering.ipynb.
'''

import numpy as np
import pandas as pd

EL_NINO = 0.5
LA_NINA = -0.5
STRONG = 1.5
MILD_THRESHOLD = 1.0

NUMERIC_FEATURES = ['ENSO_Value', 'ENSO_Strength', 'ENSO_x_Latitude', 'latitude_approx',
                    'winter_year', 'Prev_Anomaly', 'baseline_mean_temp']
CATEGORICAL_FEATURES = ['ENSO_Class', 'city_name']
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def classify(value):
    '''Label a DJF index value using the thresholds in the project README.'''
    if value >= EL_NINO:
        return 'El Nino'
    if value <= LA_NINA:
        return 'La Nina'
    return 'Neutral'


def band(value):
    '''Assign a NOAA ENSO band, the form used for reporting rather than modelling.'''
    if value >= STRONG:
        return 'Strong El Nino'
    if value >= EL_NINO:
        return 'El Nino'
    if value <= -STRONG:
        return 'Strong La Nina'
    if value <= LA_NINA:
        return 'La Nina'
    return 'Neutral'


def load_training_frame(kpi_path):
    """
    Build the modelling table from the project's processed winter KPIs.

    RONI is derived here rather than read from `enso_class`, so this works against
    any version of the file. The pipeline was rerun on RONI on 13 October 2026; before
    that the stored labels were ONI. Deriving costs nothing and removes the dependency.

    Args:
        kpi_path (str | Path): path to data/processed/winter_kpis.csv

    Returns:
        pandas.DataFrame: one row per eligible location-winter, with the target.
    """
    winters = pd.read_csv(kpi_path)
    df = winters[winters['temperature_pass']].copy()
    if 'roni_djf' not in df.columns:
        raise ValueError('winter_kpis.csv has no roni_djf column; rerun python/run_pipeline.py')
    df = df.sort_values(['city', 'winter_year']).reset_index(drop=True)

    df['ENSO_Value'] = df['roni_djf']
    df['ENSO_Class'] = df['ENSO_Value'].apply(classify)
    df['ENSO_Band'] = df['ENSO_Value'].apply(band)
    df['ENSO_Strength'] = df['ENSO_Value'].abs()
    df['ENSO_x_Latitude'] = df['ENSO_Value'] * (df['latitude_approx'] - latitude_centre(df))
    df['Mild_Winter'] = (df['temp_anomaly'] >= MILD_THRESHOLD).astype(int)

    # The first eligible winter at each location has no predecessor to lag from.
    df['Prev_Anomaly'] = df.groupby('city')['temp_anomaly'].shift(1)
    df = df.dropna(subset=['Prev_Anomaly']).reset_index(drop=True)
    return df


def latitude_centre(df):
    '''Centring constant for the interaction term, stored with the model artifact.'''
    return df['latitude_approx'].mean()


def build_row(enso_value, location, winter_year, prev_anomaly, stations, lat_centre):
    """
    Assemble a single prediction row in the shape the trained pipeline expects.

    Args:
        enso_value (float): forecast or observed DJF RONI value.
        location (str): one of the stations held in the model artifact.
        winter_year (int): year in which February falls.
        prev_anomaly (float): previous winter's temperature anomaly, in °C.
        stations (dict): station reference data from the model artifact.
        lat_centre (float): latitude centring constant from the model artifact.

    Returns:
        pandas.DataFrame: a one-row frame carrying every model feature.
    """
    station = stations[location]
    row = {
        'ENSO_Value': enso_value,
        'ENSO_Strength': abs(enso_value),
        'ENSO_x_Latitude': enso_value * (station['latitude'] - lat_centre),
        'latitude_approx': station['latitude'],
        'winter_year': winter_year,
        'Prev_Anomaly': prev_anomaly,
        'baseline_mean_temp': station['baseline_mean_temp'],
        'ENSO_Class': classify(enso_value),
        'city_name': location,
    }
    return pd.DataFrame([row], columns=FEATURES)
