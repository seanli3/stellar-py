"""ER

Classes and methods related to the Entity Resolution module.

"""

from stellar_py.payload import Payload
from typing import Dict


class StellarERPayload(Payload):
    """Payload to start an ER task

    """
    def __init__(self, session_id: str, input_dir: str, params: Dict[str, str], label: str):
        # TODO: update when finalised
        Payload.__init__(self, session_id, label)
        self.input = input_dir
        self.output = "pred/"
        self.parameters = params
