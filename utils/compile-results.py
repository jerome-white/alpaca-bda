import sys
import csv
import json
from pathlib import Path
from argparse import ArgumentParser
from dataclasses import dataclass, asdict, fields
from multiprocessing import Pool, Queue

from mylib import Logger

class ModelComparisonError(Exception):
    pass

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
            choice = float(self.preference)
            if choice == 1.5:
                self.preference = ''
            else:
                self.preference = getattr(self, f'generator_{choice:.0f}')
        except (TypeError, ValueError, AttributeError) as err:
            raise ModelComparisonError() from err

    def __iter__(self):
        for i in fields(self):
            if x.name.startswith('generator'):
                yield getattr(self, i)

    def is_baseline(self, baselines):
        assert any(x in baselines for x in self)
        assert self.generator_2 not in baselines

        return self.generator_1 in baselines

def func(incoming, outgoing, args):
    keys = [x.name for x in fields(ModelComparison)]
    baselines = set(args.baseline)

    while True:
        path = incoming.get()
        Logger.info(path)

        with path.open() as fp:
            data = json.load(fp)

        results = []
        for i in data:
            try:
                kwargs = {x: i[x] for x in keys}
                comparison = ModelComparison(**kwargs)
            except (KeyError, ModelComparisonError) as err:
                Logger.warning(f'{path}: {err}')
                continue

            if baselines and comparison.is_baseline(baselines):
                Logger.warning(f'{path}: Baseline not present')
            else:
                results.append(asdict(comparison))

        outgoing.put(results)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--baseline', action='append')
    arguments.add_argument('--results', type=Path)
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
