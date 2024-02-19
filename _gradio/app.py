import functools as ft
from pathlib import Path

import pandas as pd
import gradio as gr

#
#
#
class DataReader:
    _uncertainty = 'uncertainty'

    def __init__(self, path):
        self.df = (pd
                   .read_csv(path)
                   .assign(**{
                       self._uncertainty: lambda x: x['upper'] - x['lower'],
                   }))

    def to_frame(self, ascending):
        return (self
                .df
                .sort_values(by=['ability',  self._uncertainty],
                             ascending=[ascending, not ascending])
                .drop(columns=self._uncertainty))

#
#
#
class DataPlotter:
    def plot(self):
        raise NotImplementedError()

class RankPlotter(DataPlotter):
    _y = 'y'

    @ft.cached_property
    def y(self):
        return self.df[self._y]

    def __init__(self, reader, top=10):
        self.df = (reader
                   .to_frame(True)
                   .reset_index(drop=True)
                   .reset_index(names=self._y)
                   .tail(top)
                   .sort_values(by=self._y, ascending=False))

    def plot(self):
        ax = self.df.plot.scatter('ability', self._y)
        ax.hlines(self.y,
                  xmin=self.df['lower'],
                  xmax=self.df['upper'],
                  alpha=0.5)
        ax.set_ylabel('')
        ax.set_yticks(self.y, self.df['model'])
        ax.grid(visible=True,
                axis='both',
                alpha=0.25,
                linestyle='dashed')

        fig = ax.get_figure()
        fig.tight_layout()

        return fig

#
#
#
with gr.Blocks() as demo:
    reader = DataReader(Path('..', 'b.csv'))

    with gr.Row():
        plotter = RankPlotter(reader)
        gr.Plot(plotter.plot())

    with gr.Row():
        df = (reader
              .to_frame(False)
              .style
              .format(precision=4))
        gr.Dataframe(df)

demo.launch()
