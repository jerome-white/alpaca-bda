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
    reader = csv.DictReader(fp)
    converter = TypeConverter()

    for row in reader:
        row.update(converter(row))
        yield row

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--target', type=Path)
    args = arguments.parse_args()

    gen_kwargs = {
        'fp': sys.stdin,
    }
    dataset = Dataset.from_generator(reader, gen_kwargs=gen_kwargs)
    dataset.push_to_hub(str(args.target))
