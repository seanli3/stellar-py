import requests
from stellar_py.ingestion import StellarIngestPayload
from stellar_py.nai import StellarNAIPayload
from stellar_py.er import StellarERPayload


class SessionError(Exception):
    """Exception raised for session errors.

    Attributes:
        status_code -- http status code returned by coordinator
        message -- explanation of the error
    """
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message


class StellarTask:
    def __init__(self, addr, session_id):
        self._r = redis.StrictRedis(host=addr, port=6379, db=0, decode_responses=True)
        self._session_id = session_id

    def check_status(self):
        return self._r.get(self._session_id)

    def wait_for_result(self):
        # TODO
        pass


class StellarSession:

    _ENDPOINT_INGESTOR_START = 'ingestor/start'
    _ENDPOINT_ER_START = 'er/start'  # TODO: update when finalised
    _ENDPOINT_NAI_START = 'nai/tasks'
    _REDIS_ADDRESS = 'localhost'  # TODO: update when finalised

    _SESSIONS_INGESTOR = 'stellar:coordinator:sessions:ingestor:'
    _SESSIONS_ER = 'stellar:coordinator:sessions:er:'  # TODO: update when finalised
    _SESSIONS_NAI = 'stellar:coordinator:sessions:nai:'

    """Handles communication with Stellar Coordinator.

    Attributes:
        addr (str): Stellar Coordinator Address
        session_id (str): Unique Session ID
    """
    def __init__(self, addr, session_id):
        self._addr = addr
        self._session_id = session_id

    def _post(self, endpoint, data):
        url = '/'.join([self._addr.strip('/'), endpoint])
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        return requests.post(url, data=data, headers=headers)

    def _get_task_update_session(self, session_prefix, session_id_new):
        task = StellarTask(self._REDIS_ADDRESS, session_prefix + self._session_id)
        self._session_id = session_id_new
        return task

    def ingest_start(self, schema, sources):
        payload = StellarIngestPayload(self._session_id, schema, sources).to_json()
        r = self._post(self._ENDPOINT_INGESTOR_START, payload)
        if r.status_code == 200:
            return self._get_task_update_session(self._SESSIONS_INGESTOR, r.json()['sessionId'])
        else:
            raise SessionError(r.status_code, r.reason)

    def er_start(self, graph, params):
        payload = StellarERPayload(session_id=self._session_id, input_dir=graph.path, params=params).to_json()
        r = self._post(self._ENDPOINT_ER_START, payload)
        if r.status_code == 200:
            return self._get_task_update_session(self._SESSIONS_ER, r.json()['sessionId'])
        else:
            raise SessionError(r.status_code, r.reason)

    def nai_start(self, graph, params):
        payload = StellarNAIPayload(session_id=self._session_id, input_dir=graph.path, params=params).to_json()
        r = self._post(self._ENDPOINT_NAI_START, payload)
        if r.status_code == 200:
            return self._get_task_update_session(self._SESSIONS_NAI, r.json()['sessionId'])
        else:
            raise SessionError(r.status_code, r.reason)


def create_session(url, session_id="stellar_py_session"):
    return StellarSession(url, session_id)
