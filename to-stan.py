import sys
import json

import pandas as pd

from utils import models

def to_list(df):
    for i in df.columns:
        values = (df[i]
                  .to_numpy()
                  .tolist())
        yield (i, values)

if __name__ == '__main__':
    df = (pd
          .read_csv(sys.stdin)
          .sort_values(by=['generator_1', 'generator_2']))
    data = {
        'N': len(df),
        'K': sum(1 for _ in models(df)),
    }
    data.update(to_list(df))

    json.dump(data, sys.stdout, indent=2)
