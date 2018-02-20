"""ER

Classes and methods related to the Entity Resolution module.

"""

from stellar_py.payload import Payload
from stellar_py.graph import StellarGraph
from typing import Dict


class StellarERPayload(Payload):
    """Payload to start an ER task

    """
    def __init__(self, session_id: str, graph: StellarGraph, attribute_thresholds: Dict[str, float], label: str):
        Payload.__init__(self, session_id, label)
        self.input = graph.path

        # no parameters
        print("WARNING: Current version does not allow tuning of ER parameters. Continuing with default parameters...")
