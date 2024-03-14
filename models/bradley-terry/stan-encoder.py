import sys
import json
from pathlib import Path
from argparse import ArgumentParser

import pandas as pd

def rename(df, source, target):
    for i in df.columns:
        if i.startswith(source):
            yield (i, i.replace(source, target))

def extract(df):
    for i in df.columns:
        values = (df[i]
                  .astype(int)
                  .to_list())

        yield (i, values)

def count(df, target):
    items = list(filter(lambda x: x.startswith(target), df.columns))
    return (df
            .filter(items=items)
            .unstack()
            .nunique())

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--record', type=Path)
    args = arguments.parse_args()

    target = 'player'

    df = pd.read_csv(sys.stdin)
    columns = dict(rename(df, 'generator', target))
    df = df.rename(columns=columns)

    data = {
        'N': len(df),
        'K': count(df, target),
    }
    data.update(extract(df))

    json.dump(data, sys.stdout, indent=2)
