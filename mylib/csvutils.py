import csv
import random

class DataReader:
    def __init__(self, fp, chunks, slack=0.1):
        self.reader = csv.DictReader(fp)
        self.upper = chunks
        self.lower = round(self.upper * (1 - slack))
        self.windows = 0

    def __iter__(self):
        (window, limit) = next(self)

        for row in self.reader:
            window.append(row)
            limit -= 1
            if limit < 1:
                yield window
                self.windows += 1
                (window, limit) = next(self)

        if window:
            yield window
            self.windows += 1

    def __next__(self):
        limit = random.randint(self.lower, self.upper)
        return ([], limit)

    def __len__(self):
        return self.windows
