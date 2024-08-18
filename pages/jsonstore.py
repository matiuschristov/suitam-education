import json
import os
from pages.exception import *

class JSONStore():
    def __init__(self):
        pass
    def get(self, type, name):
        with open('/root/projects/suitam/data/{}/{}.json'.format(type, name), 'r') as f:
            try:
                return json.load(f)
            except:
                # raise SuitamException('failed to load the json file', error_code='JSON_LOAD_FAILED')
                return None
    def save(self, type, name, data):
        with open('/root/projects/suitam/data/{}/{}.json'.format(type, name), 'w') as f:
            try:
                json.dump(data, f)
            except:
                raise SuitamException('failed to dump the json file', error_code='JSON_DUMP_FAILED')
    def exists(self, type, name):
        return os.path.isfile('/root/projects/suitam/data/{}/{}.json'.format(type, name))

# os.rename('a.txt', 'b.kml')

db = JSONStore()