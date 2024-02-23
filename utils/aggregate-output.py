import sys
import csv
from pathlib import Path
from argparse import ArgumentParser
from multiprocessing import Pool

import pandas as pd

from mylib import Logger

def func(args):
    Logger.info(args)

    (*_, chain) = args.stem.split('_')
    return (pd
            .read_csv(args, comment='#', memory_map=True)
            .unstack()
            .reset_index()
            .rename(columns={
                'level_0': 'parameter',
                'level_1': 'sample',
                0: 'value',
            })
            .assign(chain=chain)
            .to_dict(orient='records'))

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--results', type=Path)
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    with Pool(args.workers) as pool:
        writer = None
        for i in pool.imap_unordered(func, args.results.rglob('*.csv')):
            if writer is None:
                writer = csv.DictWriter(sys.stdout, fieldnames=i[0])
                writer.writeheader()
            writer.writerows(i)
