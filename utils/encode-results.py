import sys
import json
from pathlib import Path
from argparse import ArgumentParser

import pandas as pd

def traverse(values, start, rev=False):
    for i in enumerate(values, start):
        if rev:
            i = tuple(reversed(i))
        yield i

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--save-encodings', type=Path)
    arguments.add_argument('--start', type=int, default=1)
    args = arguments.parse_args()

    df = pd.read_csv(sys.stdin)
    columns = {
        'prompt': (
            'instruction',
        ),
        'model': (
            'generator_1',
            'generator_2',
            'preference',
        ),
    }
    encodings = {}
    to_replace = {}

    for (k, v) in columns.items():
        values = (df
                  .filter(items=v)
                  .dropna()
                  .unstack()
                  .unique())
        encodings[k] = dict(traverse(values, args.start))
        factors = dict(traverse(values, args.start, True))
        to_replace.update({x: factors for x in v})
    df = df.replace(to_replace=to_replace)
    df.to_csv(sys.stdout, index=False)

    with args.save_encodings.open('w') as fp:
        json.dump(encodings, fp, indent=2)
