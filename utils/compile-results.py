import sys
import csv
from pathlib import Path
from datetime import datetime, timedelta
from argparse import ArgumentParser
from urllib.parse import urlparse, urlunparse

import requests

from mylib import Logger

def delorean(limit=30):
    delta = timedelta(days=1)
    today = datetime.today()

    for _ in range(limit):
        yield today.strftime('%Y%m%d')
        today -= delta

def retrieve(url):
    source = url
    path = Path(source.path)

    for i in delorean():
        p = (path
             .joinpath(f'clean_battle_{i}')
             .with_suffix('.json'))
        source = source._replace(path=str(p))
        target = urlunparse(source)
        response = requests.get(target)
        if response.ok:
            Logger.info(target)
            return response.json()

        Logger.error(f'{target}: {response.status_code}')

    raise FileNotFoundError(urlunparse(url))

def load(data, anony):
    for i in data:
        if i['anony'] or anony:
            yield i

def collect(battles, tie=''):
    models = {
        f'model_{x}': f'generator_{y}' for (x, y) in zip(('a', 'b'), (1, 2))
    }

    for b in battles:
        row = { y: b[x] for (x, y) in models.items() }
        row.update({
            'annotator': b['judge'],
            'preference':  b.get(b['winner'], tie),
        })

        yield row

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--source', type=urlparse)
    arguments.add_argument('--ignore-anony', action='store_true')
    args = arguments.parse_args()

    reader = collect(load(retrieve(args.source), args.ignore_anony))
    writer = None

    for row in reader:
        if writer is None:
            writer = csv.DictWriter(sys.stdout, fieldnames=row)
            writer.writeheader()
        writer.writerow(row)
