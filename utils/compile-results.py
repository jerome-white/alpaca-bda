import sys
import csv
import json
from argparse import ArgumentParser
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse, urlunparse

import gdown

def load(url, anony):
    with NamedTemporaryFile(mode='w') as output:
        source = gdown.download(
            url,
            output=output.name,
            quiet=True,
            fuzzy=True,
        )
        with open(source) as fp:
            data = json.load(fp)

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

    writer = None
    for row in collect(load(urlunparse(args.source), args.ignore_anony)):
        if writer is None:
            writer = csv.DictWriter(sys.stdout, fieldnames=row)
            writer.writeheader()
        writer.writerow(row)
