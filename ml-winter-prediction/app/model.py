'''
Train the mild-winter classifier and save it for serving.

Run from the ml-winter-prediction directory:

    python -m app.model

Writes app/model.joblib, which the server loads. The honest evaluation lives in
notebooks/06_07_modeling_and_evaluation.ipynb; the metrics recorded here are
recomputed so the artifact carries its own, and so the API can report them.
'''

import json
from datetime import date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.features import (CATEGORICAL_FEATURES, FEATURES, MILD_THRESHOLD, NUMERIC_FEATURES,
                          latitude_centre, load_training_frame)

HERE = Path(__file__).resolve().parent
KPI_PATH = HERE.parents[1] / 'data' / 'processed' / 'winter_kpis.csv'
RANDOM_STATE = 42
EXPECTED_ROWS = 247   # matches notebooks/05_feature_engineering.ipynb

# Load the winter data and rebuild the modelling table
df = load_training_frame(KPI_PATH)
if len(df) != EXPECTED_ROWS:
    raise ValueError(f'Expected {EXPECTED_ROWS} rows to match the notebooks, got {len(df)}. '
                     'The processed data has changed — rerun the notebooks before retraining.')

X = df[FEATURES]
y = df['Mild_Winter']
groups = df['winter_year']

# Build the pipeline. Scaling and encoding are fitted inside it, never beforehand.
pipeline = Pipeline([
    ('prep', ColumnTransformer([
        ('numeric', StandardScaler(), NUMERIC_FEATURES),
        ('categorical', OneHotEncoder(drop='first', handle_unknown='ignore'), CATEGORICAL_FEATURES),
    ])),
    ('model', LogisticRegression(max_iter=2000, random_state=RANDOM_STATE)),
])

# Score it honestly: every location in a winter stays on the same side of the split
cv = GroupKFold(n_splits=5)
oof_proba = cross_val_predict(pipeline, X, y, cv=cv, groups=groups, method='predict_proba')[:, 1]
oof_pred = (oof_proba >= 0.5).astype(int)

metrics = {
    'accuracy': accuracy_score(y, oof_pred),
    'precision': precision_score(y, oof_pred, zero_division=0),
    'recall': recall_score(y, oof_pred),
    'f1': f1_score(y, oof_pred),
    'roc_auc': roc_auc_score(y, oof_proba),
    'base_rate': y.mean(),
    'baseline_accuracy': max(y.mean(), 1 - y.mean()),
}

# Fit on everything for serving
pipeline.fit(X, y)

# Station reference data, so the API can take a location name instead of raw numbers
stations = {
    name: {
        'latitude': float(block['latitude_approx'].iloc[0]),
        'baseline_mean_temp': float(block['baseline_mean_temp'].iloc[0]),
        'region': str(block['region'].iloc[0]),
    }
    for name, block in df.groupby('city_name')
}

# Historical base rates — the part of this analysis that is actually usable
band_rates = (df.groupby('ENSO_Band')
                .agg(location_winters=('Mild_Winter', 'size'),
                     distinct_winters=('winter_year', 'nunique'),
                     mild_rate=('Mild_Winter', 'mean')))
baseline_table = {
    name: {'location_winters': int(row['location_winters']),
           'distinct_winters': int(row['distinct_winters']),
           'mild_rate': round(float(row['mild_rate']), 4)}
    for name, row in band_rates.iterrows()
}

artifact = {
    'pipeline': pipeline,
    'features': FEATURES,
    'stations': stations,
    'latitude_centre': float(latitude_centre(df)),
    'metrics': {k: round(float(v), 4) for k, v in metrics.items()},
    'baseline_table': baseline_table,
    'mild_threshold': MILD_THRESHOLD,
    'enso_index': 'RONI',
    'n_rows': int(len(df)),
    'n_winters': int(groups.nunique()),
    'trained_on': date.today().isoformat(),
}

joblib.dump(artifact, HERE / 'model.joblib')

print(f'Trained on {len(df)} location-winters from {groups.nunique()} distinct winters')
print(json.dumps(artifact['metrics'], indent=2))
print(f"\nSaved {HERE / 'model.joblib'}")
print('\nNote: out-of-fold accuracy is BELOW the do-nothing baseline. This model is '
      'published to be inspected and argued with, not to drive budget decisions. '
      'See notebooks/08_business_recommendation.ipynb.')
