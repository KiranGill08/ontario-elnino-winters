Ontario mild-winter model deployment
====================================

Complete code (including a trained model) to deploy and inference a machine learning model
(built on the Ontario El Nino winter dataset) using Docker and FastAPI.

The model predicts whether an Ontario location is heading for a mild winter from the DJF
RONI index. It is served together with its own evaluation, because the honest finding is
that it should not be used on its own — see ``notebooks/08_business_recommendation.ipynb``.

1. With terminal navigate to the root of this directory
--------------------------------------------------------

2. Train the model
------------------
Only needed if ``app/model.joblib`` is missing or the project data has changed.

.. code-block::

    python -m app.model

3. Build docker image
---------------------
.. code-block::

    docker build -t ontario-winter .

4. Run container
----------------
.. code-block::

    docker run --name winter-api -p 8000:8000 ontario-winter

5. Output will contain
----------------------
INFO:     Uvicorn running on http://0.0.0.0:8000

Use this url in chrome to see the model frontend;
use http://127.0.0.1:8000/docs for testing the model in the web interface.

6. Query model
--------------

 #. Via web interface (chrome):
        http://0.0.0.0:8000/docs -> test model

 #. Via python client:
        client.py

 #. Via curl request:
        .. code-block::

            curl -X POST http://127.0.0.1:8000/predict -H "accept: application/json" -H "Content-Type: application/json" -d '{"enso_value": 2.1, "location": "Thunder Bay", "winter_year": 2027, "prev_anomaly": 0.4}'

7. Run the tests
----------------
.. code-block::

    python -m pytest test_server.py -v

Endpoints
---------

=================  ======  =========================================================
Path               Method  Returns
=================  ======  =========================================================
``/``              GET     Service message and the model's one-line honest summary
``/health``        GET     Liveness, and whether the model artifact loaded
``/predict``       POST    Mild-winter probability, with its own quality metrics
``/baseline``      GET     Historical mild-winter rates by ENSO band
``/model-card``    GET     What the model is, what it scores, what it must not do
=================  ======  =========================================================

Request schema
--------------

Unlike a bare feature array, ``/predict`` takes named fields, because four unlabelled
numbers for a winter are easy to transpose and impossible to validate:

.. code-block::

    {
      "enso_value": 2.1,          # forecast or observed DJF RONI index
      "location": "Thunder Bay",  # one of the six study stations
      "winter_year": 2027,        # year in which February falls
      "prev_anomaly": 0.4         # last winter's anomaly at that location, in °C
    }

Derived features — ENSO strength, the ENSO-by-latitude interaction, the station's baseline
temperature — are built server side by ``app/features.py``, the same module the training
script uses. The caller cannot get them out of step with the model.

Known limitations
-----------------

The model's out-of-fold accuracy (68.4%) is **below** the do-nothing baseline (69.2%), and
its mild calls are right under half the time. It is published to be inspected, not to set
budgets. ``/model-card`` returns this in full, and every ``/predict`` response carries it.

Files
-----

=========================  ===================================================
Path                       Purpose
=========================  ===================================================
``app/features.py``        Feature construction, shared by training and serving
``app/model.py``           Trains the pipeline, scores it, writes the artifact
``app/model.joblib``       Trained pipeline plus metrics and station reference
``app/server.py``          FastAPI application
``client.py``              Inference client, scores the six stations for 2026-27
``test_server.py``         API tests, including the latitude-gradient check
``notebooks/``             The analysis that produced the model, Parts 5 to 8
=========================  ===================================================
