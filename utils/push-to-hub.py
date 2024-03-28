import sys
import csv
from pathlib import Path
from argparse import ArgumentParser

from datasets import Dataset

class TypeConverter:
    _conversions = {
        'value': lambda x: float(x if x else 'nan'),
        'chain': int,
        'sample': int,
    }

    def __call__(self, row):
        for (k, v) in self._conversions.items():
            yield (k, v(row[k]))

def reader(fp):
    def load():
        reader = csv.DictReader(fp)
        converter = TypeConverter()

        for row in reader:
            row.update(converter(row))
            yield row

    return load

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--target', type=Path)
    args = arguments.parse_args()

    dataset = Dataset.from_generator(reader(sys.stdin))
    dataset.push_to_hub(str(args.target))
