import json
import os
from pages.exception import *

jsonStorePath = '/root/projects/suitam/data'

class JSONStore():
    def __init__(self):
        pass
    def get(self, type, name):
        with open('{}/{}/{}.json'.format(jsonStorePath, type, name), 'r') as f:
            try:
                return json.load(f)
            except:
                return None
    def save(self, type, name, data):
        with open('{}/{}/{}.json'.format(jsonStorePath, type, name), 'w') as f:
            try:
                json.dump(data, f)
            except:
                raise SuitamException('failed to dump the json file', error_code='JSON_DUMP_FAILED')
    def exists(self, type, name):
        return os.path.isfile('{}/{}/{}.json'.format(jsonStorePath, type, name))

db = JSONStore()