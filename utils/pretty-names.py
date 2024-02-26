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
    (info, _) = data.values()

    return (
        info['completions_kwargs']['model_name'],
        info['pretty_name'],
    )

def configs(args):
    with Pool(args.workers) as pool:
        iterable = args.configs.rglob('config.yaml')
        yield from pool.imap_unordered(func, iterable)

def translate(source, target):
    for (k, v) in source.items():
        yield (k, target.get(v, v))

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--param-name')
    arguments.add_argument('--configs', type=Path)
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    model = 'model'
    source = json.load(sys.stdin)
    target = dict(configs(args))
    source[model] = translate(source[model], target)

    json.dump(encodings, sys.stdout, indent=2)
