import sys
import csv
import json
from pathlib import Path
from argparse import ArgumentParser
from multiprocessing import Pool, Queue

import pandas as pd

from mylib import Logger, DataReader

def func(incoming, outgoing, args):
    with args.encodings.open() as fp:
        _encodings = json.load(fp)
    _params = dict(x.split(':') for x in args.parameter)
    _parameter = 'parameter'
    _value = f'{_parameter}_value'

    while True:
        rows = incoming.get()
        Logger.info(len(rows))

        records = []
        for r in rows:
            p = r[_parameter]
            for (k, v) in _params.items():
                if p.startswith(k):
                    (name, index) = p.split('.')
                    r[_parameter] = name
                    value = _encodings[v][index]
                    break
            else:
                value = ''
            r[_value] = value
            records.append(r)

        outgoing.put(records)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--encodings', type=Path)
    arguments.add_argument('--parameter', action='append')
    arguments.add_argument('--chunk-size', type=int, default=int(1e5))
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
