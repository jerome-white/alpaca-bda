import csv
import json
import collections as cl

# class NameEncoder:
#     def __init__(self, keys, output=None):
#         self.prompt = cl.namedtuple('Prompt', keys)
#         self.output = output
#         self.names = {}

#     def __enter__(self):
#         self.names.clear()
#         return self

#     def __exit__(self, exc_type, exc_value, traceback):
#         if self.output is not None:
#             self.dump(output)

#     def __len__(self):
#         return len(self.names)

#     def transform(self, info):
#         args = map(info.get, self.prompt._fields)
#         prompt = self.prompt(*args)
#         if prompt not in self.names:
#             self.names[prompt] = len(self.names) + 1

#         return self.names[prompt]

#     def dump(self, output):
#         raise NotImplementedError()

# class PromptEncoder(NameEncoder):
#     def __iter__(self):
#         for (k, v) in self.names.items():
#             yield dict(k._asdict(), prompt_id=v)

#     def dump(self):
#         with self.utput.open('w') as fp:
#             json.dump(list(self), fp, indent=2)

# class ModelEncoder(NameEncoder):
#     def __call__(self, row):
#         for (k, v) in row.items():
#             if k.startswith(self._model):
#                 yield (k, self.transform(v))

#     def dump(self):
#         with self.output.open('w') as fp:
#             writer = csv.DictWriter(fp, fieldnames=self._fieldnames)
#             writer.writeheader()
#             for i in self.models.items():
#                 row = dict(zip(self._fieldnames, reversed(i)))
#                 writer.writerow(row)

#
#
#
class NameUnencoder(dict):
    def __init__(self, db, key, value):
        keys = (key, value)
        items = map(lambda x: tuple(map(x.get, keys)), self.build(db))
        super().__init__(items)

    def extract(self, path):
        raise NotImplementedError()

class ModelUnencoder(NameUnencoder):
    def __init__(self, db):
        super().__init__(db, 'model_id', 'prompt_id')

    def extract(self, path):
        with path.open() as fp:
            reader = csv.DictReader(fp)
            yield from reader

class PromptUnencoder(NameUnencoder):
    def __init__(self, db):
        super().__init__(db, 'prompt_id', 'instruction')

    def extract(self, path):
        with path.open() as fp:
            yield from json.load(fp)
