import itertools as it
import functools as ft
from pathlib import Path

import pandas as pd
import gradio as gr
import seaborn as sns
from scipy.special import expit

from hdi import hdi

#
#
#
def load(path):
    parameter = 'parameter'
    usecols = [
        'chain',
        'sample',
        parameter,
        'model',
        'value',
    ]

    return (pd
            .read_csv(path, usecols=usecols, memory_map=True)
            .query(f'{parameter} == "alpha"')
            .drop(columns=parameter))

def summarize(df, ci=0.95):
    def _aggregate(i, g):
        values = g['value']
        interval = hdi(values, ci)

        agg = {
            'model': i,
            'ability': values.median(),
            'uncertainty': interval.upper - interval.lower,
        }
        agg.update(interval._asdict())

        return agg

    groups = df.groupby('model', sort=False)
    records = it.starmap(_aggregate, groups)

    return pd.DataFrame.from_records(records)

def rank(df, ascending):
    return (df
            .sort_values(by=['ability',  'uncertainty'],
                         ascending=[ascending, not ascending])
            .drop(columns='uncertainty'))

def compare(df, model_1, model_2):
    mcol = 'model'
    models = [
        model_1,
        model_2,
    ]
    view = (df
            .query(f'{mcol} in @models')
            .pivot(index=['chain', 'sample'],
                   columns=mcol,
                   values='value'))

    return expit(view[model_1] - view[model_2])

#
#
#
class DataPlotter:
    def __init__(self, df):
        self.df = df

    def plot(self):
        ax = self.draw()
        ax.grid(visible=True,
                axis='both',
                alpha=0.25,
                linestyle='dashed')

        fig = ax.get_figure()
        fig.tight_layout()

        return fig

    def draw(self):
        raise NotImplementedError()

class RankPlotter(DataPlotter):
    _y = 'y'

    @ft.cached_property
    def y(self):
        return self.df[self._y]

    def __init__(self, df, top=10):
        view = rank(summarize(df), True)
        view = (view
                .reset_index(drop=True)
                .reset_index(names=self._y)
                .tail(top)
                .sort_values(by=self._y, ascending=False))
        super().__init__(view)

    def draw(self):
        ax = self.df.plot.scatter('ability', self._y)
        ax.hlines(self.y,
                  xmin=self.df['lower'],
                  xmax=self.df['upper'],
                  alpha=0.5)
        ax.set_ylabel('')
        ax.set_yticks(self.y, self.df['model'])

        return ax

class ComparisonPlotter(DataPlotter):
    def __init__(self, df, model_1, model_2, ci=0.95):
        super().__init__(compare(df, model_1, model_2))
        self.interval = hdi(self.df, ci)

    def draw(self):
        ax = sns.ecdfplot(self.df)

        (_, color, *_) = sns.color_palette()
        ax.axvline(x=self.df.median(), color=color)
        ax.axvspan(xmin=self.interval.lower,
                   xmax=self.interval.upper,
                   alpha=0.2,
                   color=color)

        return ax

def cplot(df, ci=0.95):
    def _plot(model_1, model_2):
        cp = ComparisonPlotter(df, model_1, model_2, ci)
        return cp.plot()

    return _plot

#
#
#
with gr.Blocks() as demo:
    path = Path('..', 'c.csv')
    df = load(path)

    with gr.Row():
        plotter = RankPlotter(df)
        gr.Plot(plotter.plot())

    with gr.Row():
        view = rank(summarize(df), False)
        view = (view
                .reset_index(drop=True)
                .reset_index(names='rank')
                .style
                .format(precision=4))
        gr.Dataframe(view)

    with gr.Row():
        models = df['model'].unique().tolist()
        with gr.Column():
            display = gr.Plot()
        with gr.Column():
            m1 = gr.Dropdown(choices=models, label='Model 1')
            m2 = gr.Dropdown(choices=models, label='Model 2')

            button = gr.Button(value='Compare!')
            button.click(cplot(df), inputs=[m1, m2], outputs=[display])

demo.launch()