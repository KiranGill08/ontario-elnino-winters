# Python workflow

Run `python python/run_pipeline.py` from the package root. It reads shared settings from `config.py`, calls the cleaning functions, calculates KPIs and group comparisons, and generates charts. It saves a new run folder each time.

`clean_data.py`, `calculate_kpis.py`, `eda.py` and `viz_style.py` are modules called by the runner; running those module files directly does not execute the full workflow.

See the [main README](../README.md) for installation, input paths, output tables, quality rules and examples. See [the data dictionary](../docs/data_dictionary.md) before aggregating daily files that contain repeated winter totals.
