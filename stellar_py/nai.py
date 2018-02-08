"""NAI

Classes and methods related to the Node Attribute Inference module

"""

from stellar_py.payload import Payload
from typing import Dict


class StellarNAIPayload(Payload):
    """Payload to start a NAI task

    """
    def __init__(self, session_id: str, input_dir: str, params: Dict[str, str], label: str):
        Payload.__init__(self, session_id, label)
        self.input = input_dir
        self.output = "pred/"
        self.parameters = params
