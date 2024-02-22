import sys
import csv

import pandas as pd

def each(fp):
    usecols = [
        'generator_1',
        'generator_2',
    ]
    scores = dict(zip(usecols, (1, 0)))

    usecols.append('preference')
    df = (pd
          .read_csv(fp, usecols=usecols)
          .dropna())

    for i in df.itertuples(index=False):
        result = { x: getattr(i, x) for x in scores }

        for (k, v) in result.items():
            if i.preference == v:
                result['y'] = scores[k]
                break
        else:
            raise ValueError(f'Unexpected preference: {i.preference}')

        yield result

if __name__ == '__main__':
    writer = None
    for row in each(sys.stdin):
        if writer is None:
            writer = csv.DictWriter(sys.stdout, fieldnames=row)
            writer.writeheader()
        writer.writerow(row)
