import sys
import csv
import json
import logging
from pathlib import Path
from argparse import ArgumentParser
from dataclasses import dataclass, asdict, fields
from multiprocessing import Pool, Queue

@dataclass
class ModelComparison:
    annotator: str
    instruction: str
    dataset: str
    generator_1: str
    generator_2: str
    preference: str

    def __post_init__(self):
        try:
            attr = 'generator_{}'.format(int(self.preference))
            value = getattr(self, attr)
        except (TypeError, ValueError, AttributeError):
            value = ''

        self.preference = value

def func(incoming, outgoing):
    keys = [x.name for x in fields(ModelComparison)]

    while True:
        path = incoming.get()
        logging.info(path)

        with path.open() as fp:
            data = json.load(fp)

        results = []
        for i in data:
            try:
                kwargs = {x: i[x] for x in keys}
            except KeyError as err:
                logging.error(f'{path}: {err}')
                continue
            comparison = ModelComparison(**kwargs)
            results.append(asdict(comparison))

        outgoing.put(results)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--results', type=Path)
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    incoming = Queue()
    outgoing = Queue()
    initargs = (
        outgoing,
        incoming,
    )

    with Pool(args.workers, func, initargs):
        jobs = 0
        for i in args.results.rglob('annotations.json'):
            outgoing.put(i)
            jobs += 1

        writer = None
        for _ in range(jobs):
            rows = incoming.get()
            if rows:
                if writer is None:
                    fieldnames = rows[0]
                    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
                    writer.writeheader()
                writer.writerows(rows)
