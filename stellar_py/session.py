"""Session

This module contains definitions of classes and methods are part of what constitutes the functionality of a session.
A connection to a session allows users to create and run various Stellar modules and obtain their results.
Creating a session should generally be considered the first point of access for a user to their Stellar environment.

"""

import requests
import redis
import polling
import json
import re
from typing import Dict, List, Optional, Callable, Union

from stellar_py.ingestion import StellarIngestPayload, GraphSchema, NodeMapping, EdgeMapping
from stellar_py.nai import StellarNAIPayload
from stellar_py.er import StellarERPayload
from stellar_py.graph import StellarGraph
from stellar_py.payload import Payload
from stellar_py.model import StellarMLModel


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
        if 'completed' in status:
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
    _STATUS_FAIL = 'failed'
    _REDIS_PREFIX = 'coordinator:sessions:'

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
        return (self._STATUS_COMPLETE in status) or (self._STATUS_ABORT in status) or (self._STATUS_FAIL in status)

    def wait_for_result(self, timeout: float = 0) -> StellarResult:
        """Poll status until result is available then create result

        :param timeout:     polling timeout in seconds. Set to zero to poll forever
        :return:    StellarResult
        """
        if timeout <= 0:
            polling.poll(self.is_done, step=1, poll_forever=True)
        else:
            polling.poll(self.is_done, step=1, timeout=timeout)
        return StellarResult(self.check_status(), json.loads(self._r.get(self._session_id))[self._name])


class StellarSession:
    """Handles communication with Stellar Coordinator.

    """

    _ENDPOINT_INIT = 'init'
    _TASK_INGEST = 'ingest'
    _TASK_ER = 'er'
    _TASK_NAI = 'nai'

    def __init__(self, url: str, port: int, redis_url: Optional[str] = None, redis_port: int = 6379) -> None:
        """Create a Stellar Session Object

        :param url:         Stellar Coordinator URL
        :param redis_url:   Redis Server URL
        :param redis_port:  Redis Server Port
        """
        self._url = "http://{}:{}".format(url, port)
        self._redis_url = redis_url or url
        self._redis_port = redis_port

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

    def _get_session_id(self) -> str:
        """Obtain new session ID from Stellar coordinator INIT endpoint

        :return: new session ID
        """
        response = self._get(self._ENDPOINT_INIT)
        if response.status_code == 200:
            try:
                return response.json()['sessionId']
            except json.JSONDecodeError:
                raise SessionError(500, "Failed to obtain session ID. Could not decode response from Stellar.")
            except KeyError:
                raise SessionError(500, "Failed to obtain session ID. Response from Stellar does not contain "
                                        "sessionId field.")
        else:
            raise SessionError(response.status_code, response.json()['reason'])

    def _start(self, task_name: str, create_payload: Callable[[str], Payload]) -> StellarTask:
        """Initialise a session and start a task

        :param task_name:       name of task
        :param create_payload:  callable to create payload with session ID
        :return:                StellarTask
        """
        session_id = self._get_session_id()
        payload = create_payload(session_id).to_json()
        r = self._post(task_name + '/start', payload)
        if r.status_code == 200:
            return StellarTask(self._redis_url, self._redis_port, task_name, session_id)
        else:
            raise SessionError(r.status_code, r.reason)

    def ingest_start(self, schema: GraphSchema, mappings: List[Union[NodeMapping, EdgeMapping]],
                     label: str) -> StellarTask:
        """Start an ingestion session

        :param schema:      Graph schema
        :param mappings:    List of data-source mappings
        :param label:       Label to be assigned to output graph
        :return:            StellarTask
        """
        return self._start(self._TASK_INGEST, lambda sid: StellarIngestPayload(sid, schema, mappings, label))

    def ingest(self, schema: GraphSchema, mappings: List[Union[NodeMapping, EdgeMapping]], label: str = 'ingest',
               timeout: float = 0) -> StellarGraph:
        """Start and wait for an ingestion session to produce graph

        :param schema:      Graph schema
        :param mappings:    List of data-source mappings
        :param label:       Label to be assigned to output graph
        :param timeout:     Timeout in seconds. Set to zero to poll forever.
        :return:            StellarGraph
        """
        task = self.ingest_start(schema, mappings, label)
        res = task.wait_for_result(timeout)
        if res.success:
            return StellarGraph(res.dir, label)
        else:
            raise SessionError(500, res.reason)

    def er_start(self, graph: StellarGraph, attribute_thresholds: Dict[str, float], label: str) -> StellarTask:
        """Start an Entity Resolution session

        :param graph:       Input StellarGraph object
        :param attribute_thresholds:      thresholds for each attribute as a dict - normalised between 0 and 1
        :param label:       Label to be assigned to output graph
        :return:            StellarTask
        """
        return self._start(self._TASK_ER, lambda sid: StellarERPayload(sid, graph, attribute_thresholds, label))

    def er(self, graph: StellarGraph, attribute_thresholds: Optional[Dict[str, float]] = None,
           label: str = 'er', timeout: float = 0) -> StellarGraph:
        """Start and wait for an Entity Resolution session to produce graph

        :param graph:       Input StellarGraph object
        :param attribute_thresholds:      thresholds for each attribute as a dict - normalised between 0 and 1
        :param label:       Label to be assigned to output graph
        :param timeout:     Timeout in seconds. Set to zero to poll forever.
        :return:            StellarGraph
        """
        task = self.er_start(graph, attribute_thresholds or {}, label)
        res = task.wait_for_result(timeout)
        if res.success:
            return StellarGraph(res.dir, label)
        else:
            raise SessionError(500, res.reason)

    def nai_start(self, graph: StellarGraph, model: StellarMLModel, target_attribute: str, node_type: str,
                  attributes_to_ignore: List[str], label: str) -> StellarTask:
        """Start an Node Attribute Inference session

        :param graph:               Input StellarGraph object
        :param model:               Machine Learning model with pipeline config
        :param target_attribute     Attribute to infer
        :param node_type            Type of node to infer attributes on
        :param attributes_to_ignore Attributes to ignore
        :param label:               Label to be assigned to output graph
        :return:                    StellarTask
        """
        return self._start(self._TASK_NAI, lambda sid: StellarNAIPayload(sid, graph, model, target_attribute, node_type,
                                                                         attributes_to_ignore, label))

    def predict(self, graph: StellarGraph, model: StellarMLModel, target_attribute: str, node_type: str,
                attributes_to_ignore: Optional[List[str]] = None, label: str = 'nai',
                timeout: float = 0) -> StellarGraph:
        """Predict attributes on graph elements

        :param graph:               Input StellarGraph object
        :param model:               Machine Learning model to use
        :param target_attribute     Attribute to infer
        :param node_type            Type of node to infer attributes on
        :param attributes_to_ignore Attributes to ignore
        :param label:               Label to be assigned to output graph
        :param timeout:             Timeout in seconds. Set to zero to poll forever.
        :return:                    StellarGraph with predicted attributes
        """
        task = self.nai_start(graph, model, target_attribute, node_type, attributes_to_ignore or [], label)
        res = task.wait_for_result(timeout)
        if res.success:
            print("WARNING: Current version does not allow NAI to update its graph label. "
                  "Keeping original label: {}".format(graph.label))
            return StellarGraph(res.dir, graph.label)  # NAI uses same label instead of creating new graph
        else:
            raise SessionError(500, res.reason)


def create_session(url: str, port: int = 8000) -> StellarSession:
    """Create a new Stellar Session

    :param url:     Stellar Coordinator URL
    :param port:    Stellar Coordinator Port
    :return:        new session
    """
    m = re.match("([a-zA-Z]+://)?([-a-zA-Z0-9@%_+.]+)(:[0-9]{1,4})?", url)
    return StellarSession(m.group(2), port if not m.group(3) else int(m.group(3)[1:]))
