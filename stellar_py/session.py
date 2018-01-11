import requests
from stellar_py.ingestion import StellarIngestor
from stellar_py.graph import StellarGraph

class SessionError(Exception):
    """Exception raised for session errors.

    Attributes:
        status_code -- http status code returned by coordinator
        message -- explanation of the error
    """
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

class StellarSession:
    """Handles communication with Stellar Coordinator.

    Attributes:
        addr (str): Stellar Coordinator Address
        session_id (str): Unique Session ID
    """
    def __init__(self, addr, session_id):
        self.addr = addr
        self.session_id = session_id
    def create_ingestor(self, name, schema):
        return StellarIngestor(self, name, schema)
    def post(self, endpoint, data):
        url = '/'.join([self.addr.strip('/'), endpoint])
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, data=data, headers=headers)
        if (r.status_code == 200):
            return StellarGraph(self)
        else:
            raise SessionError(r.status_code, r.reason)

def connect(addr, session_id="stellar_py_session"):
    return StellarSession(addr, session_id)
