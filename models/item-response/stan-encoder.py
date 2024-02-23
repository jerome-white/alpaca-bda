import sys
import csv
import json
from pathlib import Path
from argparse import ArgumentParser

import pandas as pd

def records(fp, encoder):
    reader = csv.DictReader(fp)
    for row in reader:
        row.update(encoder.encode(row))
        yield row

def extract(df):
    columns = {
        'model': 'p_j',
        'prompt': 'q_i',
        'correct': 'y',
    }

    for i in df.columns:
        key = columns[i]
        values = (df[i]
                  .astype(int)
                  .to_list())

        yield (key, values)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--record', type=Path)
    args = arguments.parse_args()

    with ModelNamer(output=args.record) as namer:
        df = pd.DataFrame.from_records(records(sys.stdin, namer))

        data = {
            'I': df['prompt'].nunique(),
            'J': len(namer),
            'N': len(df),
        }
        data.update(extract(df))

        json.dump(data, sys.stdout, indent=2)
