import sys

import pandas as pd

if __name__ == '__main__':
    preference = 'preference'
    (home, away) = map('generator_{}'.format, range(1, 3))

    df = (pd
          .read_csv(sys.stdin, usecols=[
              home,
              away,
              preference,
          ])
          .dropna() # remove ties
          .assign(y=lambda x: x[home] == x[preference])
          .drop(columns=preference))
    df.to_csv(sys.stdout, index=False)
