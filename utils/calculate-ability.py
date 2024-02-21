import sys
import csv
from pathlib import Path
from argparse import ArgumentParser
from multiprocessing import Pool, Queue

import pandas as pd

from mylib import Logger, hdi

def mnames(path):
    keys = (
        'model_id',
        'name',
    )

    with path.open() as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            yield tuple(map(row.get, keys))

def func(incoming, outgoing, args):
    models = dict(mnames(args.models))

    while True:
        (group, df) = incoming.get()
        Logger.info(group)

        values = df['value']
        (*_, index) = group.split('.')
        interval = hdi(values, args.ci)

        record = {
            'model': models[index],
            'ability': values.median(),
        }
        record.update(interval._asdict())

        outgoing.put(record)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--ability', default='alpha')
    arguments.add_argument('--models', type=Path)
    arguments.add_argument('--ci', type=float, default=0.95)
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
        jobs = 0
        df = pd.read_csv(sys.stdin)
        for (i, g) in df.groupby('parameter', sort=False):
            if i.startswith(args.ability):
                outgoing.put((i, g))
                jobs += 1

        writer = None
        for _ in range(jobs):
            row = incoming.get()
            if writer is None:
                writer = csv.DictWriter(sys.stdout, fieldnames=row)
                writer.writeheader()
            writer.writerow(row)
