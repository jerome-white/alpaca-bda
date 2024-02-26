import sys
import csv
import gzip
from pathlib import Path
from argparse import ArgumentParser

from datasets import Dataset

class DataReader:
    def __init__(self, source):
        self.source = source

    def __call__(self):
        with gzip.open(self.source, mode='rt') as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                for i in ('chain', 'sample'):
                    row[i] = int(row[i])

                value = row['value']
                row['value'] = float(value if value else 'nan')

                yield row

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--source', type=Path)
    arguments.add_argument('--target', type=Path)
    args = arguments.parse_args()

    reader = DataReader(args.source)
    dataset = Dataset.from_generator(reader)
    dataset.push_to_hub(str(args.target))
