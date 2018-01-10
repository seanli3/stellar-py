import requests
from stellar_py.ingestion import StellarIngestor

class StellarSession:
    def __init__(self, addr):
        self.addr = addr
        self.session_id = "pystellar"
    def create_ingestor(self, name, schema):
        return StellarIngestor(self, name, schema)
    def post(self, endpoint, data):
        url = '/'.join([self.addr.strip('/'), endpoint])
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, data=data, headers=headers)
        #TODO: do something with resp
        print(r.status_code, r.reason)
        print(r.text[:300] + '...')

def connect(addr):
    return StellarSession(addr)
