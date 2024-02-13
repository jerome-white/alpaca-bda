import sys
import csv
import collections as cl

from utils import Logger

Judgement = cl.namedtuple('Judgement', [
    'annotator',
    'prompt_id',
    'generator_1',
    'generator_2',
])

if __name__ == '__main__':
    seen = set()

    reader = csv.DictReader(sys.stdin)
    writer = csv.DictWriter(sys.stdout, fieldnames=reader.fieldnames)
    writer.writeheader()

    for row in reader:
        params = map(row.get, Judgement._fields)
        judgement = Judgement(*params)
        if judgement in seen:
            Logger.error(judgement)
            continue
        writer.writerow(row)
        seen.add(judgement)
