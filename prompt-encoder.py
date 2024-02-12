import sys
import csv
import json
import uuid
import collections as cl
from dataclasses import dataclass, asdict, fields, replace
from pathlib import Path
from argparse import ArgumentParser

@dataclass
class ModelComparison:
    annotator: str
    prompt_id: str
    generator_1: str
    generator_2: str
    preference: int

class PromptEncoder:
    def __init__(self, keys):
        self.prompt = cl.namedtuple('Prompt', keys)
        self.used = set()
        self.cache = {}

    def __iter__(self):
        for (k, v) in self.cache.items():
            yield dict(k._asdict(), prompt_id=v)

    def __next__(self):
        while True:
            pid = str(uuid.uuid4())
            if pid not in self.used:
                self.used.add(pid)
                return pid

    def transform(self, info):
        args = map(info.get, self.prompt._fields)
        prompt = self.prompt(*args)
        if prompt not in self.cache:
            self.cache[prompt] = next(self)

        return self.cache[prompt]

    def dump(self, output):
        with output.open('w') as fp:
            json.dump(list(self), fp, indent=2)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--dump', type=Path)
    args = arguments.parse_args()

    prompts = PromptEncoder([
        'instruction',
        'dataset',
    ])
    reader = csv.DictReader(sys.stdin)

    fieldnames = [x.name for x in fields(ModelComparison)]
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        params = map(row.get, fieldnames)
        comparison = ModelComparison(*params)

        prompt_id = prompts.transform(row)
        comparison = replace(comparison, prompt_id=prompt_id)

        writer.writerow(asdict(comparison))

    if args.dump is not None:
        prompts.dump(args.dump)
