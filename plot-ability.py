import sys
import sys
from pathlib import Path
from argparse import ArgumentParser

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--best', type=int)
    arguments.add_argument('--output', type=Path)
    args = arguments.parse_args()

    df = (pd
          .read_csv(sys.stdin)
          .assign(uncertainty=lambda x: x['upper'] - x['lower'])
          .sort_values(by=['ability',  'uncertainty'],
                       ascending=[True, False])
          .reset_index(drop=True)
          .reset_index(names='y'))
    if args.best:
        df = df.tail(args.best)
    df = df.sort_values(by='y', ascending=False)

    ax = df.plot.scatter('ability', 'y')
    ax.hlines(df['y'], xmin=df['lower'], xmax=df['upper'], alpha=0.5)
    ax.set_ylabel('')
    ax.set_yticks(df['y'], df['model'])

    ax.grid(visible=True,
            axis='both',
            alpha=0.25,
            linestyle='dashed')

    plt.savefig(args.output, bbox_inches='tight')
