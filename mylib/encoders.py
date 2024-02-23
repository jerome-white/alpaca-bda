import csv
import json

class NameReplacer(dict):
    def __init__(self, db, key, value):
        keys = (key, value)
        items = map(lambda x: tuple(map(x.get, keys)), self.build(db))
        super().__init__(items)

    def extract(self, path):
        raise NotImplementedError()

class ModelReplacer(NameReplacer):
    def __init__(self, db):
        super().__init__(db, 'model_id', 'prompt_id')

    def extract(self, path):
        with path.open() as fp:
            reader = csv.DictReader(fp)
            yield from reader

class PromptReplacer(NameReplacer):
    def __init__(self, db):
        super().__init__(db, 'prompt_id', 'instruction')

    def extract(self, path):
        with path.open() as fp:
            yield from json.load(fp)
