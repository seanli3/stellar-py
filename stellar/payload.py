"""Payload

Generic payload class definition. Specific Payload classes for Stellar modules can inherit from this.

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

import json


class Payload:
    """Generic payload class

    """
    def __init__(self, session_id: str, label: str) -> None:
        """Initialise

        :param session_id:  Session ID
        :param label:       Output graph label
        """
        self.sessionId = session_id
        self.label = label

    def to_json(self) -> str:
        """Turn payload into JSON string

        :return: JSON string
        """
        return json.dumps(self.__dict__, indent=4)
