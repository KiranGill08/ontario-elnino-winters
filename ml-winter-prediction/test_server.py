'''
Tests for the mild-winter model API.

Run from the ml-winter-prediction directory:

    python -m pytest test_server.py -v
'''

from fastapi.testclient import TestClient

from app.server import app

client = TestClient(app)


def test_root_reports_the_model_honestly():
    response = client.get('/')
    assert response.status_code == 200
    assert 'not a basis for setting a winter maintenance budget' in response.json()['honest_summary']


def test_health_confirms_the_model_loaded():
    body = client.get('/health').json()
    assert body['status'] == 'ok'
    assert body['model_loaded'] is True
    assert body['enso_index'] == 'RONI'


def test_predict_returns_a_probability_and_its_caveats():
    response = client.post('/predict', json={'enso_value': 2.1, 'location': 'Thunder Bay',
                                             'winter_year': 2027, 'prev_anomaly': 0.4})
    assert response.status_code == 200
    body = response.json()
    assert 0.0 <= body['mild_probability'] <= 1.0
    assert body['predicted_class'] in ('mild', 'not mild')
    assert body['enso_band'] == 'Strong El Nino'
    assert body['guidance']          # a prediction never ships without its caveat


def test_strong_el_nino_scores_higher_in_the_north_than_the_south():
    '''The latitude gradient is the project's central finding; the model should carry it.'''
    def probability(location):
        return client.post('/predict', json={'enso_value': 2.1, 'location': location,
                                             'winter_year': 2027,
                                             'prev_anomaly': 0.0}).json()['mild_probability']

    assert probability('Thunder Bay') > probability('Windsor')


def test_unknown_location_is_rejected():
    response = client.post('/predict', json={'enso_value': 1.0, 'location': 'Vancouver',
                                             'winter_year': 2027, 'prev_anomaly': 0.0})
    assert response.status_code == 422


def test_out_of_range_enso_value_is_rejected():
    response = client.post('/predict', json={'enso_value': 99, 'location': 'Ottawa',
                                             'winter_year': 2027, 'prev_anomaly': 0.0})
    assert response.status_code == 422


def test_baseline_names_the_five_winter_caveat():
    body = client.get('/baseline').json()
    assert body['by_enso_band']['Strong El Nino']['distinct_winters'] == 5
    assert 'five distinct winters' in body['note']


def test_moderate_el_nino_is_not_treated_as_a_weak_strong_el_nino():
    '''The relationship is a step at +1.5, not a slope. The base rates must show it.'''
    rates = client.get('/baseline').json()['by_enso_band']
    assert rates['El Nino']['mild_rate'] < rates['Neutral']['mild_rate']
    assert rates['Strong El Nino']['mild_rate'] > 2 * rates['El Nino']['mild_rate']


def test_model_card_states_it_loses_to_the_baseline():
    body = client.get('/model-card').json()
    assert body['metrics']['accuracy'] < body['metrics']['baseline_accuracy']
    assert any('below the do-nothing baseline' in l for l in body['known_limitations'])
