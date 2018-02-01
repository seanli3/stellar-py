import requests
import redis
import polling
import json

from stellar_py.ingestion import StellarIngestPayload
from stellar_py.nai import StellarNAIPayload
from stellar_py.er import StellarERPayload
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


class StellarResult:
    def __init__(self, status, payload):
        self.status = status
        if status == 'completed':
            self.success = True
            self.dir = payload['outputDir']
        else:
            self.success = False
            self.reason = payload['reason'] or 'Timed out at: ' + payload['lastHeartbeatTime']


class StellarTask:
    def __init__(self, addr, port, session_id, payload_id):
        self._r = redis.StrictRedis(host=addr, port=port, db=0, decode_responses=True)
        self._session_id = session_id
        self._payload_id = payload_id

    def check_status(self):
        return json.loads(self._r.get(self._session_id))['status']

    def wait_for_result(self):
        polling.poll(lambda: (self.check_status() == 'completed') or (self.check_status() == 'aborted'),
                     step=1, poll_forever=True)
        return StellarResult(self.check_status(), json.loads(self._r.get(self._payload_id)))


class StellarSession:
    # TODO: add label and auto to payloads

    _ENDPOINT_INIT = 'session/create'  # TODO: update when finalised
    _ENDPOINT_INGESTOR_START = 'ingestor/start'
    _ENDPOINT_ER_START = 'er/start'  # TODO: update when finalised
    _ENDPOINT_NAI_START = 'nai/tasks'

    _SESSIONS_INGESTOR = 'stellar:coordinator:sessions:ingestor:'
    _SESSIONS_ER = 'stellar:coordinator:sessions:er:'  # TODO: update when finalised
    _SESSIONS_NAI = 'stellar:coordinator:sessions:nai:'

    _PAYLOADS_INGESTOR = 'stellar:coordinator:payloads:ingestor:'
    _PAYLOADS_ER = 'stellar:coordinator:payloads:er:'  # TODO: update when finalised
    _PAYLOADS_NAI = 'stellar:coordinator:payloads:nai:'

    """Handles communication with Stellar Coordinator.

    Attributes:
        addr (str): Stellar Coordinator Address
        session_id (str): Unique Session ID
    """
    def __init__(self, addr, redis_addr='localhost', redis_port=6379):
        self._addr = addr
        self._redis_addr = redis_addr  # TODO: update when finalised
        self._redis_port = redis_port  # TODO: update when finalised
        response = self._get(self._ENDPOINT_INIT)
        if response.status_code == 200:
            self._session_id = response.json()['sessionId']
        else:
            raise SessionError(response.status_code, response.json()['reason'])

    def _get(self, endpoint, params=None):
        url = '/'.join([self._addr.strip('/'), endpoint])
        return requests.get(url, params=params) if params else requests.get(url)

    def _post(self, endpoint, data):
        url = '/'.join([self._addr.strip('/'), endpoint])
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        return requests.post(url, data=data, headers=headers)

    def _get_task_update_session(self, session_prefix, payload_prefix, session_id_new):
        task = StellarTask(self._redis_addr, self._redis_port,
                           session_prefix + self._session_id, payload_prefix + self._session_id)
        self._session_id = session_id_new
        return task

    def ingest_start(self, schema, sources, label):
        payload = StellarIngestPayload(self._session_id, schema, sources, label).to_json()
        r = self._post(self._ENDPOINT_INGESTOR_START, payload)
        if r.status_code == 200:
            return self._get_task_update_session(
                self._SESSIONS_INGESTOR, self._PAYLOADS_INGESTOR, r.json()['sessionId'])
        else:
            raise SessionError(r.status_code, r.reason)

    def ingest(self, schema, sources, label='ingest'):
        task = self.ingest_start(schema, sources, label)
        res = task.wait_for_result()
        if res.success:
            return StellarGraph(res.dir)
        else:
            raise SessionError(500, res.reason)

    def er_start(self, graph, params, label):
        payload = StellarERPayload(self._session_id, graph.path, params, label).to_json()
        r = self._post(self._ENDPOINT_ER_START, payload)
        if r.status_code == 200:
            return self._get_task_update_session(self._SESSIONS_ER, self._PAYLOADS_ER, r.json()['sessionId'])
        else:
            raise SessionError(r.status_code, r.reason)

    def er(self, graph, params, label='er'):
        task = self.er_start(graph, params, label)
        res = task.wait_for_result()
        if res.success:
            return StellarGraph(res.dir)
        else:
            raise SessionError(500, res.reason)

    def nai_start(self, graph, params, label):
        payload = StellarNAIPayload(self._session_id, graph.path, params, label).to_json()
        r = self._post(self._ENDPOINT_NAI_START, payload)
        if r.status_code == 200:
            return self._get_task_update_session(self._SESSIONS_NAI, self._PAYLOADS_NAI, r.json()['sessionId'])
        else:
            raise SessionError(r.status_code, r.reason)

    def nai(self, graph, params, label='nai'):
        task = self.nai_start(graph, params, label)
        res = task.wait_for_result()
        if res.success:
            return StellarGraph(res.dir)
        else:
            raise SessionError(500, res.reason)


def create_session(url):
    return StellarSession(url)
