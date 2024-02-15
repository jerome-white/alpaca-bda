import sys
import csv
import json
from pathlib import Path
from argparse import ArgumentParser

import pandas as pd

class ModelNamer:
    _model = 'generator_'
    _fieldnames = (
        'model_id',
        'name',
    )
    
    def __init__(self, output=None):
        self.output = output
        self.index = 0
        self.models = {}

    def __enter__(self):
        self.models.clear()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.output is not None:
            with self.output.open('w') as fp:
                writer = csv.DictWriter(fp, fieldnames=self._fieldnames)
                writer.writeheader()
                for i in self.models.items():
                    row = dict(zip(self._fieldnames, reversed(i)))
                    writer.writerow(row)

    def __len__(self):
        return len(self.models)

    def __getitem__(self, item):
        if item not in self.models:
            self.models[item] = self.index
            self.index += 1

        return self.models[item]

    def __call__(self, row):
        for (k, v) in row.items():
            if k.startswith(self._model):
                yield (k, self[v])

def records(fp, namer):
    reader = csv.DictReader(fp)
    for row in reader:
	row.update(namer(row))
        yield row

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--record', type=Path)
    args = arguments.parse_args()

    outcomes = (
        'win_1',
        'win_2',
        'ties',
    )

    with ModelNamer(output=args.record) as namer:
        df = pd.DataFrame.from_records(records(sys.stdin, namer))

        data = {
            'N': len(df),
            'K': len(namer),
        }
        for i in outcomes:
            data[i] = df[i].to_numpy().tolist()
        json.dump(data, sys.stdout, indent=2)
