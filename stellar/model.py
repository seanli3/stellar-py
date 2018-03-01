"""Models

Import Machine-Learning models to configure and use with Stellar

"""

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

