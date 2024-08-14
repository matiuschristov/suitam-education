import json
import os

class JSONStore():
    def __init__(self):
        pass
    def get(self, type, name):
        with open('/root/projects/suitam/data/{}/{}.json'.format(type, name), 'r') as f:
            return json.load(f)
    def save(self, type, name, data):
        with open('/root/projects/suitam/data/{}/{}.json'.format(type, name), 'w') as f:
            json.dump(data, f)
    def exists(self, type, name):
        return os.path.isfile('/root/projects/suitam/data/{}/{}.json'.format(type, name))

# os.rename('a.txt', 'b.kml')