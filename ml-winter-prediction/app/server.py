from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib

from app.features import band, build_row

artifact = joblib.load('app/model.joblib')

model = artifact['pipeline']
stations = artifact['stations']
metrics = artifact['metrics']

GUIDANCE = ('Out-of-fold accuracy is below the do-nothing baseline and precision is under 50%. '
            'Use this probability as weak context alongside the historical base rates at '
            '/baseline. It is not a basis for setting a winter maintenance budget.')

app = FastAPI(
    title='Ontario mild-winter model API',
    description=('Predicts whether an Ontario location is heading for a mild winter, from the '
                 'DJF RONI index. Published with its own evaluation attached, because the '
                 'honest answer is that it should not be used on its own.'),
    version='1.0.0',
)


class WinterRequest(BaseModel):
    '''One winter at one location, described only by what is knowable in advance.'''

    enso_value: float = Field(..., ge=-4, le=4,
                              description='Forecast or observed DJF RONI index value',
                              json_schema_extra={'example': 2.1})
    location: str = Field(..., description='Station name held by the model',
                          json_schema_extra={'example': 'Thunder Bay'})
    winter_year: int = Field(..., ge=1982, le=2100,
                             description='Year in which February falls',
                             json_schema_extra={'example': 2027})
    prev_anomaly: float = Field(..., ge=-15, le=15,
                                description="Previous winter's temperature anomaly in °C",
                                json_schema_extra={'example': 0.4})


@app.get('/')
def read_root():
    return {'message': 'Ontario mild-winter model API',
            'docs': '/docs',
            'honest_summary': GUIDANCE}


@app.get('/health')
def health():
    '''Liveness check, including whether the model artifact actually loaded.'''
    return {'status': 'ok',
            'model_loaded': model is not None,
            'trained_on': artifact['trained_on'],
            'enso_index': artifact['enso_index']}


@app.post('/predict')
def predict(request: WinterRequest):
    """
    Predicts whether a location is heading for a mild winter.

    A mild winter is one at least 1.0 °C above that location's 1991-2020 baseline.

    Args:
        request (WinterRequest): the ENSO value, location, winter year and
        previous winter's anomaly.
        e.g. {"enso_value": 2.1, "location": "Thunder Bay",
              "winter_year": 2027, "prev_anomaly": 0.4}

    Returns:
        dict: the predicted class, its probability, the historical rate for that
        ENSO band, and the model's own limitations.
    """
    if request.location not in stations:
        raise HTTPException(status_code=422,
                            detail=f'Unknown location. Known: {sorted(stations)}')

    row = build_row(request.enso_value, request.location, request.winter_year,
                    request.prev_anomaly, stations, artifact['latitude_centre'])
    probability = float(model.predict_proba(row)[0, 1])
    enso_band = band(request.enso_value)
    historical = artifact['baseline_table'].get(enso_band)

    return {
        'predicted_class': 'mild' if probability >= 0.5 else 'not mild',
        'mild_probability': round(probability, 4),
        'location': request.location,
        'enso_band': enso_band,
        'historical_rate_for_this_band': historical,
        'model_quality': {'roc_auc': metrics['roc_auc'],
                          'precision': metrics['precision'],
                          'accuracy': metrics['accuracy'],
                          'do_nothing_accuracy': metrics['baseline_accuracy']},
        'guidance': GUIDANCE,
    }


@app.get('/baseline')
def baseline():
    '''Historical mild-winter rates by ENSO band — the defensible output of this project.'''
    return {'mild_threshold_c': artifact['mild_threshold'],
            'overall_base_rate': metrics['base_rate'],
            'by_enso_band': artifact['baseline_table'],
            'note': ('Only the Strong El Nino band separates from the base rate, and it rests '
                     'on five distinct winters. Moderate El Nino winters were mild LESS often '
                     'than neutral ones: the relationship is a step at +1.5, not a slope.')}


@app.get('/model-card')
def model_card():
    '''What the model is, what it scores, and what it must not be used for.'''
    return {
        'task': 'Binary classification: will this location-winter be at least 1.0 °C above its '
                '1991-2020 baseline?',
        'model': 'Logistic regression with standardisation and one-hot encoding',
        'training_data': {'rows': artifact['n_rows'], 'distinct_winters': artifact['n_winters'],
                          'locations': sorted(stations), 'index': artifact['enso_index']},
        'evaluation': 'GroupKFold on winter_year — every location in a winter stays in the same '
                      'fold. Splitting rows at random instead raises a random forest from 0.55 '
                      'to 0.87 AUC on this data.',
        'metrics': metrics,
        'known_limitations': [
            'Out-of-fold accuracy is below the do-nothing baseline.',
            'Precision is under 50%: mild calls are wrong more often than right.',
            'The DJF index is only final in March, so these scores are an upper bound on what '
            'is achievable from an autumn forecast.',
            'Every usable finding rests on five strong El Nino winters.',
            'Association, not cause. Other drivers also act on Ontario winters.',
        ],
        'intended_use': 'Teaching, inspection and discussion. Not budget decisions.',
    }
