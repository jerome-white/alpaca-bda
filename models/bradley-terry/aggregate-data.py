import sys
from argparse import ArgumentParser

import pandas as pd

from mylib import Logger

#
#
#
class NullGrouper:
    def __init__(self, df, column):
        self.df = df
        self.column = column

    def __call__(self, idx):
        value = self.df.loc[idx, self.column]
        return pd.notnull(value)

#
#
#
class PreferenceHandler:
    def __iter__(self):
        raise NotImplementedError()

class WinHandler(PreferenceHandler):
    def __init__(self, lhs, rhs):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs

    def __iter__(self):
        yield lambda x: x[self.lhs].eq(x[self.rhs])

# class SpreadTieHandler(PreferenceHandler):
#     def __init__(self, tie=0.5):
#         super().__init__()
#         self.tie = tie

#     def __iter__(self):
#         yield lambda _: self.tie

class AddTieHandler(PreferenceHandler):
    def __iter__(self):
        for i in range(2):
            yield lambda _: bool(i)

#
#
#
def decide(df, lhs, rhs, ties):
    preferences = {
        True: WinHandler(lhs, rhs),
    }
    if ties:
        preferences[False] = AddTieHandler()
        # preferences[False] = SpreadTieHandler(1)

    grouper = NullGrouper(df, rhs)
    for (i, g) in df.groupby(grouper):
        if i in preferences:
            Logger.info(f'{i}: n={len(g)}')
            handler = preferences[i]
            for y in handler:
                yield g.assign(y=y)

#
#
#
if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--with-ties', action='store_true')
    args = arguments.parse_args()

    preference = 'preference'
    (home, away) = map('generator_{}'.format, range(1, 3))
    usecols = [
        home,
        away,
        preference,
    ]

    df = pd.read_csv(sys.stdin, usecols=usecols)
    Logger.info(f'Before: N={len(df)}')
    df = (pd
          .concat(decide(df, home, preference, args.with_ties))
          .drop(columns=preference))
    Logger.info(f'After: N={len(df)}')

    df.to_csv(sys.stdout, index=False)
