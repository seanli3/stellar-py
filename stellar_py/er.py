from stellar_py.payload import Payload


class StellarERPayload(Payload):
    def __init__(self, session_id, input_dir, params, label='er', auto=False):
        # TODO: update when finalised
        Payload.__init__(self, session_id, label, auto)
        self.input = input_dir
        self.output = "pred/"
        self.parameters = params
