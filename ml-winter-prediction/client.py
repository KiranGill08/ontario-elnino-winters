'''
Script for inferencing the deployed model

Scores the six study locations for winter 2026-27, using NOAA's advisory of a
very strong El Nino. Run the container first, then: python client.py
'''

import json
import requests

# enso_value, location, winter_year, prev_anomaly
data = [[2.1, 'Windsor', 2027, 0.4],
        [2.1, 'London', 2027, 0.6],
        [2.1, 'Toronto Pearson', 2027, 0.5],
        [2.1, 'Ottawa', 2027, 0.3],
        [2.1, 'Sudbury', 2027, 0.2],
        [2.1, 'Thunder Bay', 2027, 0.1]]

url = 'http://0.0.0.0:8000/predict'

predictions = []
for record in data:
    payload = {'enso_value': record[0], 'location': record[1],
               'winter_year': record[2], 'prev_anomaly': record[3]}
    payload = json.dumps(payload)
    response = requests.post(url, data=payload,
                             headers={'Content-Type': 'application/json'})
    result = response.json()
    predictions.append((result['location'], result['predicted_class'],
                        result['mild_probability']))

for location, predicted, probability in predictions:
    print(f'{location:18} {predicted:9} p={probability:.3f}')

print()
print('Historical context for the same question:')
print(json.dumps(requests.get('http://0.0.0.0:8000/baseline').json()['by_enso_band'], indent=2))
print()
print('Read /model-card before acting on any of the above.')
