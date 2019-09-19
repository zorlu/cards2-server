from app.settings import logger
from datetime import datetime


class Command(object):
    items = None
    meta = {}

    def __init__(self, meta=None):
        self.items = []
        if meta:
            self.meta = meta

    def add(self, key, data):
        self.items.append({
            'key': key,
            'data': data,
            'seq': len(self.items)
        })
        """
        # print("first-command", self.items[0]['key'], "items", len(self.items))
        if self.items[0]['key'] == "attacked":
            print("WRONG", self.items)
            raise Exception("Doktor Bu ne?")
        """

        return self

    def finalize(self):
        result = None
        if len(self.items):
            result = self.meta
            result['type'] = "commands"
            result['commands'] = self.items
            self.meta = {}

        return result
