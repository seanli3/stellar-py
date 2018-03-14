"""NAI

Classes and methods related to the Node Attribute Inference module

"""

__copyright__ = """

    This file is part of stellar-py, Stellar Python Client.

    Copyright 2018 CSIRO Data61

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

"""
__license__ = "Apache 2.0"

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
