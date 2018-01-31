from stellar_py.payload import Payload


class StellarERPayload(Payload):
    def __init__(self, session_id, input_dir, params):
        # TODO: update when finalised
        self.sessionId = session_id
        self.input = input_dir
        self.output = "pred/"
        self.parameters = params
