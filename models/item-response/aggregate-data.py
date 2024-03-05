import sys
import csv
from argparse import ArgumentParser
from multiprocessing import Pool, Queue

import pandas as pd

from mylib import Logger, DataReader

class Assessor:
    def __init__(self, model):
        self.columns = (
            model,
            'preference',
        )

    def __call__(self, x):
        (m, p) = map(x.get, self.columns)
        return (p
                .combine_first(m)
                .eq(m))

#
#
#
def func(incoming, outgoing, args):
    correct = 'correct'
    items = {
        'prompt': 'instruction',
        'model': args.target,
        correct: None,
    }
    columns = { y: x for (x, y) in items.items() if y is not None }
    kwargs = {
        correct: Assessor(args.target),
    }

    while True:
        rows = incoming.get()
        Logger.info(len(rows))

        records = (pd
                   .DataFrame
                   .from_records(rows)
                   .assign(**kwargs)
                   .rename(columns=columns)
                   .filter(items=items)
                   .to_dict(orient='records'))
        outgoing.put(records)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--target', default='generator_2')
    arguments.add_argument('--chunk-size', type=int, default=100000)
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
        reader = DataReader(sys.stdin, args.chunk_size)
        for rows in reader:
            outgoing.put(rows)

        writer = None
        for _ in range(len(reader)):
            rows = incoming.get()
            if writer is None:
                writer = csv.DictWriter(sys.stdout, fieldnames=rows[0])
                writer.writeheader()
            writer.writerows(rows)
