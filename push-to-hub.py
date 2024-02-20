import sys
from pathlib import Path
from argparse import ArgumentParser

import pandas as pd
from datasets import Dataset

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--source', type=Path)
    arguments.add_argument('--target', type=Path)
    args = arguments.parse_args()

    df = pd.read_csv(args.source, memory_map=True)

    dataset = Dataset.from_pandas(df)
    dataset.push_to_hub(str(args.target))
