import sys
import csv
import json
from pathlib import Path
from argparse import ArgumentParser
from multiprocessing import Pool, Queue

import pandas as pd

from mylib import Logger, DataReader

def get_baselines(baselines, encodings):
    with encodings.open() as fp:
        models = (json
                  .load(fp)
                  .get('model'))
    lookup = dict(map(reversed, models.items()))
    yield from map(lookup.get, args.baseline)

def func(incoming, outgoing, args):
    mcols = list(map('generator_{}'.format, range(1, 3)))
    baselines = set(get_baselines(args.baseline, args.encodings))
    assert all(baselines)

    while True:
        rows = incoming.get()
        Logger.info(len(rows))

        results = []
        for i in rows:
            models = set(map(i.get, mcols))
            try:
                (respondent, ) = models.difference(baselines)
            except ValueError:
                # raise LookupError(f'Cannot establish baseline: {models}')
                Logger.error(f'Cannot establish baseline: {models}')
                continue
            correct = i['preference'] not in baselines

            results.append({
                'prompt': i['instruction'],
                'model': respondent,
                'correct': int(correct),
            })

        outgoing.put(results)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--baseline', action='append')
    arguments.add_argument('--encodings', type=Path)
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
