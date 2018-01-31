import json


class Payload:
    def to_json(self):
        return json.dumps(self.__dict__, indent=4)
