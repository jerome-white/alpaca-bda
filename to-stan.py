import sys
import json

import pandas as pd

def to_list(df):
    for i in df.columns:
        values = (df[i]
                  .to_numpy()
                  .tolist())
        yield (i, values)

if __name__ == '__main__':
    df = pd.read_csv(sys.stdin)

    items = list(map('model_{}'.format, range(1, 3)))
    models = (df
              .filter(items=items)
              .unstack()
              .unique())

    data = {
        'N': len(df),
        'K': len(models),
    }
    data.update(to_list(df))

    json.dump(data, sys.stdout, indent=2)
