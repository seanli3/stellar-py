import json
from stellar_py.payload import Payload


class StellarNAIPayload(Payload):
    def __init__(self, session_id, input_dir, params):
        self.sessionId = session_id
        self.input = input_dir
        self.output = "pred/"
        self.parameters = params
