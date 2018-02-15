"""Payload

Generic payload class definition. Specific Payload classes for Stellar modules can inherit from this.

"""

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
        self.auto = 'false'

    def to_json(self) -> str:
        """Turn payload into JSON string

        :return: JSON string
        """
        return json.dumps(self.__dict__, indent=4)
