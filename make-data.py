import sys
import csv
import collections as cl
from argparse import ArgumentParser
from multiprocessing import Pool, Queue

import pandas as pd

from utils import Logger, models

GroupKey = cl.namedtuple('GroupKey', 'generator_1, generator_2')
Result = cl.namedtuple('Result',
                       GroupKey._fields + ('win_1', 'win_2'),
                       defaults=[0, 0])

class ModelGrouper:
    def __init__(self, df):
        self.pairs = df.filter(items=GroupKey._fields)
        self.order = dict(map(reversed, enumerate(sorted(models(df)))))

    def __call__(self, idx):
        (g1, g2) = self.pairs.iloc[idx]
        (o1, o2) = map(self.order.get, (g1, g2))

        return (g1, g2) if o1 < o2 else (g2, g1)

def func(args):
    (group, df) = args
    Logger.info(' '.join(group))

    gdict = group._asdict()
    result = Result(**gdict)
    indices = { y: x[-1] for (x, y) in gdict.items() }

    for (i, g) in df.groupby('preference', sort=False):
        kwargs = {
            f'win_{indices[i]}': len(g),
        }
        result = result._replace(**kwargs)

    return result

def each(fp):
    df = pd.read_csv(fp)
    grouper = ModelGrouper(df)

    for (i, g) in df.groupby(grouper, sort=False):
        key = GroupKey(*i)
        yield (key, g)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    with Pool(args.workers) as pool:
        writer = csv.DictWriter(sys.stdout, fieldnames=Result._fields)
        writer.writeheader()
        for i in pool.imap_unordered(func, each(sys.stdin)):
            writer.writerow(i._asdict())
