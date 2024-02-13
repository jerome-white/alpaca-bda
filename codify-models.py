import sys
import csv
import collections as cl
from pathlib import Path
from argparse import ArgumentParser

class ModelNamer:
    _model = 'generator_'
    _fieldnames = (
        'model_id',
        'name',
    )
    
    def __init__(self, start=1):
        self.index = start
        self.names = {}

    def __call__(self, row):
        for (k, v) in row.items():
            if k.startswith(self._model):
                if v not in self.names:
                    self.names[v] = self.index
                    self.index += 1

                yield (k, self.names[v])

    def dump(self, path):
        with path.open('w') as fp:
            writer = csv.DictWriter(fp, fieldnames=self._fieldnames)
            writer.writeheader()
            for i in self.names.items():
                row = dict(zip(self._fieldnames, reversed(i)))
                writer.writerow(row)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--record', type=Path)
    args = arguments.parse_args()

    namer = ModelNamer()
    
    reader = csv.DictReader(sys.stdin)
    writer = csv.DictWriter(sys.stdout, fieldnames=reader.fieldnames)
    writer.writeheader()

    for row in reader:
        models = dict(namer(row))
        row.update(models)
        writer.writerow(row)

    if args.record is not None:
        namer.dump(args.record)
