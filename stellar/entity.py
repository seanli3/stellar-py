"""Entity Resolvers

Import Machine-Learning models to configure and use with Stellar

"""

from typing import Dict


class StellarEntityResolver:
    """Base class for Stellar ML Models

    """
    def __init__(self, params: Dict) -> None:
        self.params = params


class EntityResolution(StellarEntityResolver):
    """Entity Resolution using SERF

    """
    def __init__(self):
        StellarEntityResolver.__init__(self, {})
