import sys
import csv
from pathlib import Path
from argparse import ArgumentParser

import pandas as pd

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--save-encodings', type=Path)
    arguments.add_argument('--start', type=int, default=1)
    args = arguments.parse_args()

    df = pd.read_csv(sys.stdin)
    columns = (
        ('instruction', ),
        ('generator_1', 'generator_2', 'preference'),
    )
    to_replace = {}

    for cols in columns:
        values = (df
                  .filter(items=cols)
                  .dropna()
                  .unstack()
                  .unique())
        factors = dict(map(reversed, enumerate(values, args.start)))
        to_replace.update({x: factors for x in cols})
    df = df.replace(to_replace=to_replace)
    df.to_csv(sys.stdout, index=False)

    if args.save_encodings is not None:
        fieldnames = (
            'ftype',
            'code',
            'value',
        )
        with args.save_encodings.open('w') as fp:
            json.dump(to_replace, fp, indent=2)
