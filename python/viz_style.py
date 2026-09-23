"""Shared chart appearance. No chart changes the analytical data."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

COLORS = {'El Nino': '#b5482d', 'Neutral': '#64748b', 'La Nina': '#2866a6'}


def apply_style():
    plt.rcParams.update({'font.size': 10, 'axes.titlesize': 12,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'figure.facecolor': 'white', 'axes.facecolor': 'white',
                         'savefig.dpi': 160})


def finish(fig, path):
    fig.tight_layout(rect=(0, 0, 1, .95))
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)
"""Shared chart appearance. No chart changes the analytical data."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

COLORS = {'El Nino': '#b5482d', 'Neutral': '#64748b', 'La Nina': '#2866a6'}


def apply_style():
    plt.rcParams.update({'font.size': 10, 'axes.titlesize': 12,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'figure.facecolor': 'white', 'axes.facecolor': 'white',
                         'savefig.dpi': 160})


def finish(fig, path, note=None):
    fig.tight_layout(rect=(0, 0.03 if note else 0, 1, .95))
    if note:  # footnote explaining excluded winters and record limits
        fig.text(.01, .005, note, fontsize=8, color='#64748b', va='bottom')
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)