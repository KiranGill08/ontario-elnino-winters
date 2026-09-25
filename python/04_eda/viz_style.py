"""Shared chart appearance. No chart changes the analytical data.

Charts are always saved as PNG files. When the code runs inside a Jupyter
notebook, each chart is also displayed inline as it is made.
"""
import sys
from pathlib import Path
import matplotlib

IN_NOTEBOOK = 'ipykernel' in sys.modules
if not IN_NOTEBOOK:
    matplotlib.use('Agg')  # scripts: write files only, never open windows
import matplotlib.pyplot as plt

COLORS = {'El Nino': '#b5482d', 'Neutral': '#64748b', 'La Nina': '#2866a6'}


def apply_style():
    plt.rcParams.update({'font.size': 10, 'axes.titlesize': 12,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'figure.facecolor': 'white', 'axes.facecolor': 'white',
                         'savefig.dpi': 160})


def close(fig):
    """Show the chart inline when in a notebook, then free its memory."""
    if IN_NOTEBOOK:
        from IPython.display import display
        display(fig)
    plt.close(fig)


def save_chart_data(frame, png_path):
    """Save the exact rows a chart plots, named after the chart (snow_days_by_enso.png ->
    snow_days_by_enso.csv). Pipeline and notebook runs: <run>/data/chart_data/.
    Standalone runs: a chart_data/ folder next to the image."""
    png_path = Path(png_path)
    folder = (png_path.parent.parent / 'data' / 'chart_data' if png_path.parent.name == 'figures'
              else png_path.parent / 'chart_data')
    folder.mkdir(parents=True, exist_ok=True)
    frame.to_csv(folder / f'{png_path.stem}.csv', index=False, float_format='%.6g')


def finish(fig, path, note=None, data=None):
    if data is not None:
        save_chart_data(data, path)
    fig.tight_layout(rect=(0, 0.03 if note else 0, 1, .95))
    if note:  # footnote explaining excluded winters and record limits
        fig.text(.01, .005, note, fontsize=8, color='#64748b', va='bottom')
    fig.savefig(path, bbox_inches='tight')
    close(fig)