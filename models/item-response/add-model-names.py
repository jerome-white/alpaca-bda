import sys
import csv
from pathlib import Path
from argparse import ArgumentParser
from multiprocessing import Pool, Queue

from mylib import Logger, DataReader, ModelUnencoder, PromptUnencoder

#
#
#
def func(incoming, outgoing, args):
    _parameter = 'parameter'

    pu = PromptUnencoder(args.prompts)
    _unencoders = {
        'alpha': pu,
        'beta': pu,
        'theta': ModelUnencoder(args.models),
    }

    while True:
        samples = incoming.get()
        Logger.info(len(samples))

        records = []
        for s in samples:
            param = s.get(_parameter)

            parts = param.split('.')
            n = len(parts)
            if n == 1:
                value = ''
            elif n == 2:
                (name, index) = parts
                s[_parameter] = name
                value = (_unencoders
                         .get(name)
                         .get(int(index)))
                assert value, f'{name} {index}'
            else:
                raise ValueError(f'Too many dots in parameter name: {param}')

            s['name'] = value
            records.append(s)
        outgoing.put(records)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--models', type=Path)
    arguments.add_argument('--prompts', type=Path)
    arguments.add_argument('--chunk-size', type=int, default=100000)
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    incoming = Queue()
    outgoing = Queue()
    initargs = (
        outgoing,
        incoming,
        args,
    )

    with Pool(args.workers, func, initargs):
        reader = DataReader(sys.stdin, args.chunk_size)
        for rows in reader:
            outgoing.put(rows)

        writer = None
        for _ in range(len(reader)):
            rows = incoming.get()
            if writer is None:
                writer = csv.DictWriter(sys.stdout, fieldnames=rows[0])
                writer.writeheader()
            writer.writerows(rows)
