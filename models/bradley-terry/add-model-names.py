import sys
import csv
from pathlib import Path
from argparse import ArgumentParser
from multiprocessing import Pool, Queue

from utils import Logger

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
    _dot = '.'
    _parameter = 'parameter'
    _models = dict(mnames(args.models))

    while True:
        samples = incoming.get()
        Logger.info(len(samples))

        records = []
        for s in samples:
            param = s[_parameter]
            if param.find(_dot) >= 0:
                (name, index) = param.split(_dot)
                s[_parameter] = name
                model = _models[index]
            else:
                model = ''
            s['model'] = model
            records.append(s)
        outgoing.put(records)

class DataReader:
    def __init__(self, fp, chunks):
        self.reader = csv.DictReader(fp)
        self.chunks = chunks
        self.windows = 0

    def __iter__(self):
        window = []

        for row in self.reader:
            window.append(row)
            if len(window) >= self.chunks:
                yield window
                window = []
                self.windows += 1

        if window:
            yield window
            self.windows += 1

    def __len__(self):
        return self.windows

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--models', type=Path)
    arguments.add_argument('--chunk-size', type=int, default=10000)
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
