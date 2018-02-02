from stellar_py.payload import Payload


class StellarNAIPayload(Payload):
    def __init__(self, session_id, input_dir, params, label='nai', auto=False):
        Payload.__init__(self, session_id, label, auto)
        self.input = input_dir
        self.output = "pred/"
        self.parameters = params
