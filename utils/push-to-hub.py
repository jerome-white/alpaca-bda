import sys
import csv
from pathlib import Path
from argparse import ArgumentParser

from datasets import Dataset

class DataReader:
    _conversions = {
        'value': lambda x: float(x if x else 'nan'),
        'chain': int,
        'sample': int,
    }
    
    def __init__(self, fp):
        self.reader = csv.DictReader(fp)

    def __call__(self):
        for row in self.reader:
            row.update(self.as_types(row))
            yield row

    def as_types(self, row):
        for (k, v) in self._conversions.items():
            yield (k, v(row[k]))

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--target', type=Path)
    args = arguments.parse_args()

    reader = DataReader(sys.stdin)
    dataset = Dataset.from_generator(reader)
    dataset.push_to_hub(str(args.target))
