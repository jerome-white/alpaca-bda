import sys
import json
from pathlib import Path
from argparse import ArgumentParser
from multiprocessing import Pool

import yaml

from mylib import Logger

def func(args):
    Logger.info(args)

    with args.open() as fp:
        data = yaml.safe_load(fp)

    for (k, v) in data.items():
        v = v.get('pretty_name', k)
        return (k, v)

def configs(args):
    with Pool(args.workers) as pool:
        iterable = args.configs.rglob('configs.yaml')
        yield from pool.imap_unordered(func, iterable)

def translate(source, target):
    for (k, v) in source.items():
        if v in target:
            yield (k, target[v])

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--configs', type=Path)
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    model = 'model'
    source = json.load(sys.stdin)
    target = dict(configs(args))
    source[model].update(translate(source[model], target))

    json.dump(source, sys.stdout, indent=2)
