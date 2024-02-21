import sys
import csv
from pathlib import Path
from argparse import ArgumentParser
from multiprocessing import Pool, Queue

import pandas as pd

from utils import Logger

def func(incoming, outgoing):
    columns = {
        'level_0': 'parameter',
        'level_1': 'sample',
        0: 'value',
    }

    while True:
        path = incoming.get()
        Logger.info(path)

        (*_, chain) = path.stem.split('_')
        records = (pd
                   .read_csv(path, comment='#', memory_map=True)
                   .unstack()
                   .reset_index()
                   .rename(columns=columns)
                   .assign(chain=chain)
                   .to_dict(orient='records'))

        outgoing.put(records)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--results', type=Path)
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    incoming = Queue()
    outgoing = Queue()
    initargs = (
        outgoing,
        incoming,
    )

    with Pool(args.workers, func, initargs):
        jobs = 0
        for i in args.results.rglob('*.csv'):
            outgoing.put(i)
            jobs += 1

        writer = None
        for _ in range(jobs):
            rows = incoming.get()
            if rows:
                if writer is None:
                    fieldnames = rows[0]
                    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
                    writer.writeheader()
                writer.writerows(rows)
