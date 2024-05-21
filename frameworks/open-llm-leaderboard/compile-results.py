import sys
import csv
from pathlib import Path
from argparse import ArgumentParser
from dataclasses import dataclass, fields
from urllib.parse import urlparse, urlunparse
from multiprocessing import Pool, Queue

import awswrangler as wr

from mylib import Logger

@dataclass
class AuthorModel:
    author: str
    model: str

    def __str__(self):
        return str(self.to_path())

    def to_path(self):
        args = (x or y for (x, y) in zip((self.author, self.model), ('/', '')))
        return Path(*args)

@dataclass
class Groups:
    task: str
    metric: str
    category: str

    def __eq__(self, other):
        if self.task.startswith(other.task):
            for i in ('category', 'metric'):
                (lhs, rhs) = (getattr(x, i) for x in (self, other))
                if lhs != rhs:
                    break
            else:
                return True

        return False

class DataIterator:
    def __init__(self, task, metric, category=None):
        self.group = Groups(task, metric, category or '')
        self.groupby = [ x.name for x in fields(Groups) ]

    def __call__(self, df):
        grouped = df.groupby(
            self.groupby,
            sort=False,
            dropna=False,
            observed=True,
        )
        for (i, g) in grouped:
            group = Groups(*i)
            if group == self.group:
                yield (i, g)

def func(incoming, outgoing, args):
    walk = DataIterator(args.task, args.metric, args.category)

    while True:
        df = incoming.get()
        records = []

        for (i, g) in walk(df):
            Logger.info(i)
            for j in g.itertuples(index=False):
                am = AuthorModel(j.author, j.model)
                records.append({
                    'model': str(am),
                    'question': i.prompt,
                    'score': i.value,
                })

        outgoing.put(records)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--bucket', type=urlparse)
    arguments.add_argument('--task', default='hendrycks')
    arguments.add_argument('--category')
    arguments.add_argument('--metric', default='acc')
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
        path = urlunparse(args.bucket._replace(path=''))
        frames = wr.s3.read_parquet(
            path=path,
            path_root=args.bucket.path,
            dataset=True,
            chunked=int(1e5),
        )
        for i in frames:
            outgoing.put(i)
            jobs += 1

        writer = None
        for _ in range(jobs):
            rows = incoming.get()
            if rows:
                if writer is None:
                    writer = csv.DictWriter(sys.stdout, fieldnames=rows[0])
                    writer.writeheader()
                writer.writerow(rows)
