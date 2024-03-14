import sys
import json
from pathlib import Path
from argparse import ArgumentParser
from dataclasses import dataclass
from multiprocessing import Pool, Queue

import numpy as np
import pandas as pd

from mylib import Logger

@dataclass
class Encoding:
    group: str
    codes: dict
    df: pd.DataFrame

    def values(self):
        yield (self.group, self.codes)

@dataclass
class DataGroup:
    group: str
    df: pd.DataFrame

    def __str__(self):
        cols = ', '.join(self.df.columns)
        return f'{self.group}: {cols}'

    def encode(self, start):
        categories = pd.Categorical(self.df.unstack())

        codes = np.where(categories.codes < 0, pd.NA, categories.codes + start)
        values = np.hsplit(codes, len(self.df.columns))
        to_replace = dict(zip(self.df.columns, values))

        codes = dict(enumerate(categories.categories, start))
        df = self.df.assign(**to_replace)

        return Encoding(self.group, codes, df)

class EncodingRecorder:
    def __init__(self, output):
        self.output = output
        self.encodings = {}

    def __enter__(self):
        self.encodings.clear()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        with self.output.open('w') as fp:
            json.dump(self.encodings, fp, indent=2)

    def push(self, encoding):
        self.encodings.update(encoding.values())

def func(incoming, outgoing, args):
    while True:
        data = incoming.get()
        Logger.info(data)
        outgoing.put(data.encode(args.start))

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--save-encodings', type=Path)
    arguments.add_argument('--start', type=int, default=1)
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    incoming = Queue()
    outgoing = Queue()
    initargs = (
        outgoing,
        incoming,
        args,
    )

    with Pool(args.workers, func, initargs):
        groups = {
            'prompt': (
                'instruction',
            ),
            'model': (
                'generator_1',
                'generator_2',
                'preference',
            ),
        }
        df = pd.read_csv(sys.stdin)

        for (k, v) in groups.items():
            data = DataGroup(k, df.filter(items=v))
            outgoing.put(data)

        with EncodingRecorder(args.save_encodings) as recorder:
            for _ in range(len(groups)):
                encoding = incoming.get()
                recorder.push(encoding)
                df.update(encoding.df)
        df.to_csv(sys.stdout, index=False)
