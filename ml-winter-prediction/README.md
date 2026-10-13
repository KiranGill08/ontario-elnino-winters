# Can we anticipate a mild Ontario winter?

The predictive arm of the Ontario El Niño study, built as an end-to-end project: the
analysis that produced the model, the model itself, and the service that serves it.

The main study asks what past El Niño winters *looked like*. This asks whether that history
is strong enough to **anticipate** anything before a winter begins.

**Business question:** before a winter starts, can we tell an Ontario municipality it is
heading for a mild winter, so salt, plough and overtime budgets can be set with better
information?

**Answer:** not for an individual winter. The honest model is *less* accurate than assuming
no winter will ever be mild. One narrow finding does survive, and it is in Notebook 3.

## Layout

```
ml-winter-prediction/
  notebooks/        the analysis, Parts 5 to 8
  app/
    features.py     feature construction, shared by training and serving
    model.py        trains the pipeline, scores it, writes the artifact
    model.joblib    trained pipeline plus metrics and station reference data
    server.py       FastAPI application
  client.py         inference client
  test_server.py    API tests
  Dockerfile
  requirements.txt
  readme.rst        deployment instructions
```

## The analysis

| Notebook | Covers | Produces |
|---|---|---|
| `notebooks/05_feature_engineering.ipynb` | Part 5 — Feature Engineering | `winter_features.csv` |
| `notebooks/06_07_modeling_and_evaluation.ipynb` | Parts 6 and 7 — Modeling and Evaluation | `winter_predictions.csv` |
| `notebooks/08_business_recommendation.ipynb` | Part 8 — Business Recommendation | the recommendation |

Each numbered question appears as its own heading, with the code and a written answer
beneath it. Run them in order.

**Data:** the project's own pipeline output, `../data/processed/winter_kpis.csv`. Nothing
is synthetic. After eligibility rules and a lagged feature, **247 location-winters across
44 distinct winters** reach the model.

**Target:** `Mild_Winter` — at least 1.0 °C above that location's own 1991–2020 baseline.
Base rate 31%.

## The service

```bash
python -m app.model          # train, if app/model.joblib is missing
docker build -t ontario-winter .
docker run --name winter-api -p 8000:8000 ontario-winter
```

Then `http://127.0.0.1:8000/docs`, or `python client.py`. Full instructions in
[readme.rst](readme.rst).

Every `/predict` response ships with the model's own quality metrics and a guidance string
saying it must not drive budget decisions. `/baseline` returns the historical rates that
*are* defensible, and `/model-card` returns the limitations in full.

## Five things worth reading for

1. **Notebook 2, Q4 — the most important result here.** Six locations share each winter and
   carry an identical ENSO value, so splitting rows at random puts the same winter on both
   sides. Done that way a random forest scores **0.87 AUC**. Split by winter, the same model
   scores **0.55**. Logistic regression barely moves — it never had the capacity to memorise
   winters in the first place.

2. **Notebook 2, Part 7 Q6** — the honest model is 0.8 points *less* accurate than assuming
   no winter is ever mild, while still having a real AUC of 0.61. Neither fact is visible
   from accuracy alone.

3. **Notebook 1, Q5 — a boundary that cost a winter.** NOAA's thresholds are inclusive, so
   an index of exactly +1.5 *is* a strong El Niño. `pd.cut`'s default is exclusive at the
   top, which silently dropped winter 1987 and made the strong band look like four winters
   instead of five. The banding is now written out to match the published definition.

4. **Notebook 1, Section 0b — a config change that had not reached the data.**
   `python/config.py` switched the primary index to RONI on 22 September, but
   `data/processed/winter_kpis.csv` is generated, and nobody reran the pipeline — so for
   three weeks the committed data still said `enso_index = 'ONI'` and disagreed with the
   project's own convention on 6 of 45 winters. **Resolved: the pipeline was rerun on
   13 October 2026.** The notebooks still derive RONI themselves and now verify it against
   the stored labels, so they stay correct against any checkout.

5. **Notebook 3, Section 3** — a mild winter is not a winter without cold snaps. In the
   strong El Niño winters Thunder Bay still recorded 17 to 33 days at or below −20 °C. That
   is the finding most likely to be misread, and the most expensive to get wrong.

## What the record does support

Everything usable rests on the **five** strong El Niño winters since 1982 — 1983, 1987,
1992, 1998 and 2016. Roughly seven in ten location-winters in those events came in at least
1 °C above normal, against a 31% base rate.

The relationship is a **step, not a slope**: moderate El Niño winters were mild *less* often
than neutral ones. Nothing happens until the index clears +1.5.

And it is a northern effect. El Niño minus other winters, south to north: Windsor −10
points, London −2, Toronto −7, Ottawa +10, Sudbury +22, Thunder Bay +24. An Ontario-wide
statement would average these and describe nowhere.

Five events cannot establish a rate. Winter 2026-27, if it verifies as strong, would be the
sixth — which makes measuring it the highest-value thing the project can do next.
