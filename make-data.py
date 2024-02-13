import sys
import csv
import collections as cl
from argparse import ArgumentParser
from multiprocessing import Pool, Queue

import pandas as pd

from utils import Logger

GroupKey = cl.namedtuple('GroupKey', 'model_1, model_2')
Result = cl.namedtuple('Result',
                       GroupKey._fields + ('win_1', 'win_2'),
                       defaults=[0, 0])

class ModelGrouper:
    _col = 'generator'
    
    def __init__(self, df):
        items = [ f'{self._col}_{i}' for i in range(1, 3) ]
        self.models = df.filter(items=items)

    def __call__(self, idx):
        models = (self
                  .models
                  .iloc[idx]
                  .to_numpy())
        
        return tuple(sorted(models))

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
    df = pd.read_csv(sys.stdin)
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
