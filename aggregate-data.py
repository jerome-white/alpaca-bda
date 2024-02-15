import sys
import csv
from argparse import ArgumentParser
from dataclasses import dataclass, asdict, fields
from multiprocessing import Pool

import pandas as pd

from utils import Logger, models

@dataclass
class GroupKey:
    generator_1: str
    generator_2: str

@dataclass
class Result(GroupKey):
    win_1: int = 0
    win_2: int = 0
    ties:  int = 0

class ModelGrouper:
    def __init__(self, df):
        self.pairs = df.filter(items=list(attrs(GroupKey)))
        self.order = dict(map(reversed, enumerate(sorted(models(df)))))

    def __call__(self, idx):
        (g1, g2) = self.pairs.iloc[idx]
        (o1, o2) = map(self.order.get, (g1, g2))

        return (g1, g2) if o1 < o2 else (g2, g1)

def attrs(dclass):
    yield from (x.name for x in fields(dclass))

def tally(df, indices):
    for (i, g) in df.groupby('preference', sort=False):
        key = 'ties' if pd.isnull(i) else f'win_{indices[i]}'
        yield (key, len(g))

def func(args):
    (group, df) = args
    Logger.info(' '.join(group.values()))

    indices = { y: x[-1] for (x, y) in group.items() }
    wins = dict(df, indices)

    return Result(**group, **wins)

def each(fp):
    df = pd.read_csv(fp)
    grouper = ModelGrouper(df)

    for (i, g) in df.groupby(grouper, sort=False):
        key = GroupKey(*i)
        yield (asdict(key), g)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    with Pool(args.workers) as pool:
        fieldnames = list(attrs(Result))
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        for i in pool.imap_unordered(func, each(sys.stdin)):
            writer.writerow(asdict(i))
