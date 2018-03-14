"""Models

Import Machine-Learning models to configure and use with Stellar

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

from typing import Dict


class StellarMLModel:
    """Base class for Stellar ML Models

    """
    def __init__(self, params: Dict) -> None:
        self.params = params


class Node2Vec(StellarMLModel):
    """Node2Vec ML Model

    """
    def __init__(self, metric_learning: bool = False) -> None:
        if metric_learning:
            StellarMLModel.__init__(self, {'pipelineFilename': 'pipeline_full.json'})
        else:
            StellarMLModel.__init__(self, {'pipelineFilename': 'pipeline_basic.json'})


class GCN(StellarMLModel):
    """GCN ML Model

    """
    def __init__(self) -> None:
        StellarMLModel.__init__(self, {'pipelineFilename': 'pipeline_gcn.json'})

