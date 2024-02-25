import sys
import csv
import json
from pathlib import Path

import pandas as pd

class DataExtractor:
    def __init__(self, df, usecols):
        self.df = df
        self.usecols = usecols

    def __iter__(self):
        raise NotImplementedError()

class ConstantsExtractor(DataExtractor):
    def __init__(self, df):
        super().__init__(df, {
            'prompt': 'I',
            'model': 'J',
        })

    def __iter__(self):
        for (k, v) in self.usecols.items():
            data = self.df[k].nunique()
            yield (v, data)

class ValuesExtractor(DataExtractor):
    def __init__(self, df):
        super().__init__(df, {
            'model': 'p_j',
            'prompt': 'q_i',
            'correct': 'y',
        })

    def __iter__(self):
        for i in self.df.columns:
            key = self.usecols[i]
            values = (df[i]
                      .astype(int)
                      .to_list())

            yield (key, values)

if __name__ == '__main__':
    extractors = (
        ConstantsExtractor,
        ValuesExtractor,
    )
    df = pd.read_csv(sys.stdin)

    data = dict(N=len(df))
    for i in extractors:
        e = i(df)
        data.update(e)

    json.dump(data, sys.stdout, indent=2)
