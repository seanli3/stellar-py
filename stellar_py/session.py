"""Session

This module contains definitions of classes and methods are part of what constitutes the functionality of a session.
A connection to a session allows users to create and run various Stellar modules and obtain their results.
Creating a session should generally be considered the first point of access for a user to their Stellar environment.

"""

import requests
import redis
import polling
import json
from typing import Dict, List

from stellar_py.ingestion import StellarIngestPayload, GraphSchema, DataSource
from stellar_py.nai import StellarNAIPayload
from stellar_py.er import StellarERPayload
from stellar_py.graph import StellarGraph


class SessionError(Exception):
    """Exception raised for session errors.

    Attributes:
        status_code: http status code returned by coordinator
        message: explanation of the error
    """
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message


class StellarResult:
    """Contains result information from a completed or failed task

        Attributes:
            status (str):   'completed' | 'aborted'
            success (bool): flag for success
            dir (str):      path to graph
            reason (str):   reason for failure
    """
    def __init__(self, status: str, payload: Dict[str, str]) -> None:
        """Initialise

        :param status:      Status from Redis
        :param payload:     Payload dict from Redis
        """
        self.status = status
        if status == 'completed':
            self.success = True
            self.dir = payload['output']
        else:
            self.success = False
            self.reason = payload['error']


class StellarTask:
    """Contains methods to obtain status and result of a task performed by a Stellar module

    """

    _STATUS_COMPLETE = 'completed'
    _STATUS_ABORT = 'aborted'
    _REDIS_PREFIX = 'stellar:coordinator:sessions:'

    def __init__(self, url: str, port: int, name: str, session_id: str) -> None:
        """Initialise

        :param url:         Redis URL
        :param port:        Redis Port
        :param name:        task name ( ingest | er | nai )
        :param session_id:  session key
        """
        self._r = redis.StrictRedis(host=url, port=port, db=0, decode_responses=True)
        self._session_id = self._REDIS_PREFIX + session_id
        self._name = name

    def check_status(self) -> str:
        """Check status of task

        :return:    'init' | 'running' | 'completed' | 'aborted'
        """
        return json.loads(self._r.get(self._session_id))['status']

    def is_done(self) -> bool:
        """Check if task is completed or aborted

        :return: true if done
        """
        status = self.check_status()
        return (status == self._STATUS_COMPLETE) or (status == self._STATUS_ABORT)

    def wait_for_result(self) -> StellarResult:
        """Poll status until result is available then create result

        :return:    StellarResult
        """
        polling.poll(self.is_done, step=1, poll_forever=True)
        return StellarResult(self.check_status(), json.loads(self._r.get(self._session_id))[self._name])


class StellarSession:
    """Handles communication with Stellar Coordinator.

    """

    _ENDPOINT_INIT = 'session/create'  # TODO: update when finalised
    _ENDPOINT_INGESTOR_START = 'ingestor/start'
    _ENDPOINT_ER_START = 'er/start'  # TODO: update when finalised
    _ENDPOINT_NAI_START = 'nai/tasks'

    _TASK_INGESTOR = 'ingest'
    _TASK_ER = 'er'
    _TASK_NAI = 'nai'

    def __init__(self, url: str, redis_url: str = 'localhost', redis_port: int = 6379) -> None:
        """Create a Stellar Session Object

        :param url:         Stellar Coordinator URL
        :param redis_url:   Redis Server URL
        :param redis_port:  Redis Server Port
        """
        self._url = url
        self._redis_url = redis_url  # TODO: update when finalised
        self._redis_port = redis_port  # TODO: update when finalised
        response = self._get(self._ENDPOINT_INIT)
        if response.status_code == 200:
            self._session_id = response.json()['sessionId']
        else:
            raise SessionError(response.status_code, response.json()['reason'])

    def _get(self, endpoint: str, params: dict = None) -> requests.Response:
        """GET request to the coordinator/endpoint

        :param endpoint:    Specific endpoint
        :param params:      Parameters for the request
        :return:            Response
        """
        url = '/'.join([self._url.strip('/'), endpoint])
        return requests.get(url, params=params) if params else requests.get(url)

    def _post(self, endpoint: str, data: str) -> requests.Response:
        """POST request to the coordinator/endpoint

        :param endpoint:    Specific endpoint
        :param data:        Data to POST
        :return:            Response
        """
        url = '/'.join([self._url.strip('/'), endpoint])
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        return requests.post(url, data=data, headers=headers)

    def _get_task_update_session(self, task_name: str, session_id_new: str) -> StellarTask:
        """Create a reference to a newly created task, and update stale session with new session ID

        :param session_prefix:  Prefix string specific to session key
        :param task_name:       Task name
        :param session_id_new:  New session ID
        :return:                StellarTask
        """
        task = StellarTask(self._redis_url, self._redis_port, task_name, self._session_id)
        self._session_id = session_id_new
        return task

    def ingest_start(self, schema: GraphSchema, sources: List[DataSource], label: str) -> StellarTask:
        """Start an ingestion session

        :param schema:      Graph schema
        :param sources:     List of data-source mappings
        :param label:       Label to be assigned to output graph
        :return:            StellarTask
        """
        payload = StellarIngestPayload(self._session_id, schema, sources, label).to_json()
        r = self._post(self._ENDPOINT_INGESTOR_START, payload)
        if r.status_code == 200:
            return self._get_task_update_session(self._TASK_INGESTOR, r.json()['sessionId'])
        else:
            raise SessionError(r.status_code, r.reason)

    def ingest(self, schema: GraphSchema, sources: List[DataSource], label: str = 'ingest') -> StellarGraph:
        """Start and wait for an ingestion session to produce graph

        :param schema:      Graph schema
        :param sources:     List of data-source mappings
        :param label:       Label to be assigned to output graph
        :return:            StellarGraph
        """
        task = self.ingest_start(schema, sources, label)
        res = task.wait_for_result()
        if res.success:
            return StellarGraph(res.dir)
        else:
            raise SessionError(500, res.reason)

    def er_start(self, graph: StellarGraph, params: Dict[str, str], label: str) -> StellarTask:
        """Start an Entity Resolution session

        :param graph:       Input StellarGraph object
        :param params:      Parameters for ER
        :param label:       Label to be assigned to output graph
        :return:            StellarTask
        """
        payload = StellarERPayload(self._session_id, graph.path, params, label).to_json()
        r = self._post(self._ENDPOINT_ER_START, payload)
        if r.status_code == 200:
            return self._get_task_update_session(self._TASK_ER, r.json()['sessionId'])
        else:
            raise SessionError(r.status_code, r.reason)

    def er(self, graph: StellarGraph, params: Dict[str, str], label: str = 'er') -> StellarGraph:
        """Start and wait for an Entity Resolution session to produce graph

        :param graph:       Input StellarGraph object
        :param params:      Parameters for ER
        :param label:       Label to be assigned to output graph
        :return:            StellarGraph
        """
        task = self.er_start(graph, params, label)
        res = task.wait_for_result()
        if res.success:
            return StellarGraph(res.dir)
        else:
            raise SessionError(500, res.reason)

    def nai_start(self, graph: StellarGraph, params: Dict[str, str], label: str) -> StellarTask:
        """Start an Node Attribute Inference session

        :param graph:       Input StellarGraph object
        :param params:      Parameters for NAI
        :param label:       Label to be assigned to output graph
        :return:            StellarTask
        """
        payload = StellarNAIPayload(self._session_id, graph.path, params, label).to_json()
        r = self._post(self._ENDPOINT_NAI_START, payload)
        if r.status_code == 200:
            return self._get_task_update_session(self._TASK_NAI, r.json()['sessionId'])
        else:
            raise SessionError(r.status_code, r.reason)

    def nai(self, graph: StellarGraph, params: Dict[str, str], label: str = 'nai') -> StellarGraph:
        """Start and wait for an Node Attribute Inference session to produce graph

        :param graph:       Input StellarGraph object
        :param params:      Parameters for NAI
        :param label:       Label to be assigned to output graph
        :return:            StellarGraph
        """
        task = self.nai_start(graph, params, label)
        res = task.wait_for_result()
        if res.success:
            return StellarGraph(res.dir)
        else:
            raise SessionError(500, res.reason)


def create_session(url: str) -> StellarSession:
    """Create a new Stellar Session

    :param url:     Stellar Coordinator URL
    :return:        new session
    """
    return StellarSession(url)
