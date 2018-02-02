import json


class Payload:
    def __init__(self, session_id, label, auto):
        self.sessionId = session_id
        self.label = label
        self.auto = 'true' if auto else 'false'

    def to_json(self):
        return json.dumps(self.__dict__, indent=4)
