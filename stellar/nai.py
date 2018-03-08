"""NAI

Classes and methods related to the Node Attribute Inference module

"""

from stellar.payload import Payload
from stellar.graph import StellarGraph
from stellar.model import StellarMLModel
from typing import List


class StellarNAIPayload(Payload):
    """Payload to start a NAI task

    """
    def __init__(self, session_id: str, graph: StellarGraph, model: StellarMLModel, target_attribute: str,
                 node_type: str, attributes_to_ignore: List[str], label: str):
        Payload.__init__(self, session_id, label)
        self.input = graph.path
        self.inputs = {
            'in_data': {
                'dataset_name': graph.label
            }
        }
        self.parameters = {
            'convert_epgm': 'True',
            'target_attribute': target_attribute,
            'node_type': node_type,
            'attributes_to_ignore': attributes_to_ignore
        }
        self.pipelineFilename = model.params.get('pipelineFilename', 'pipeline_basic.json')
