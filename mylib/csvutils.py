import csv

class DataReader:
    def __init__(self, fp, chunks):
        self.reader = csv.DictReader(fp)
        self.chunks = chunks
        self.windows = 0

    def __iter__(self):
        window = []

        for row in self.reader:
            window.append(row)
            if len(window) >= self.chunks:
                yield window
                window = []
                self.windows += 1

        if window:
            yield window
            self.windows += 1

    def __len__(self):
        return self.windows
