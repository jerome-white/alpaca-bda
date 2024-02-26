import sys
import csv
import json
from pathlib import Path

import pandas as pd

#
#
#
class DataExtractor:
    def __init__(self, df, usecols):
        self.df = df
        self.usecols = usecols

    def __iter__(self):
        for (k, v) in self.usecols.items():
            values = self.extract(self.df[k])
            yield (v, values)

    def extract(self, values):
        raise NotImplementedError()

class ConstantsExtractor(DataExtractor):
    def __init__(self, df):
        super().__init__(df, {
            'prompt': 'I',
            'model': 'J',
        })

    def extract(self, values):
        return values.nunique()

class ValuesExtractor(DataExtractor):
    def __init__(self, df):
        super().__init__(df, {
            'model': 'p_j',
            'prompt': 'q_i',
            'correct': 'y',
        })

    def extract(self, values):
        return values.astype(int).to_list()

#
#
#
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
