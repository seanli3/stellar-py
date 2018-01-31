import json


class StellarNAIPayload:
    def __init__(self, session_id, input_dir, params):
        self.sessionId = session_id
        self.input = input_dir
        self.output = "pred/"
        self.parameters = params

    def to_json(self):
        return json.dumps(self.__dict__, indent=4)
