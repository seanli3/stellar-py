"""Entity Resolvers

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
