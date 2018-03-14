"""Test for ER"""

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

from stellar.er import *
from stellar.entity import *
from stellar.session import SessionError
import stellar as st
from redis import StrictRedis
import httpretty
import pytest


stellar_addr = "http://localhost:3000"
stellar_addr_er = stellar_addr + "/er/start"
stellar_addr_session = stellar_addr + "/init"


def test_er_payload():
    graph = StellarGraph('graph.epgm', 'test_er_ori')
    payload = StellarERPayload(session_id='test_session', graph=graph, resolver=EntityResolution(),
                               attribute_thresholds={}, label='test_er')
    assert payload.sessionId == 'test_session'
    assert payload.input == 'graph.epgm'
    assert payload.label == 'test_er'


@httpretty.activate
def test_er_start():
    httpretty.register_uri(httpretty.POST, stellar_addr_er,
                           body=u'{"sessionId": "melon"}')
    httpretty.register_uri(httpretty.GET, stellar_addr_session, body=u'{"sessionId": "dummy_session_id"}')
    ss = st.create_session(url=stellar_addr)
    task = ss.er_start(graph=StellarGraph('graph.epgm', 'test_er_ori'), resolver=EntityResolution(),
                       attribute_thresholds={}, label='test_er')
    assert task._session_id == "coordinator:sessions:dummy_session_id"


@httpretty.activate
def test_er(monkeypatch):
    httpretty.register_uri(httpretty.POST, stellar_addr_er)
    httpretty.register_uri(httpretty.GET, stellar_addr_session, body=u'{"sessionId": "dummy_session_id"}')
    monkeypatch.setattr(
        'test_er.StrictRedis.get',
        lambda *_: u'{"status": "er completed", "er": {"output": "test_path.epgm", "error":""}}')
    ss = st.create_session(url=stellar_addr)
    graph = ss.entity_resolution(StellarGraph('graph.epgm', 'test_er_ori'), EntityResolution(), label='test_er')
    assert graph.path == "test_path.epgm"
    assert graph.label == 'test_er_ori'  # label unchanged


@httpretty.activate
def test_er_error(monkeypatch):
    httpretty.register_uri(httpretty.POST, stellar_addr_er, body=u'{"sessionId": "melon"}')
    httpretty.register_uri(httpretty.GET, stellar_addr_session, body=u'{"sessionId": "dummy_session_id"}')
    monkeypatch.setattr(
        'test_er.StrictRedis.get',
        lambda *_: u'{"status": "aborted", "er": {"output": "", "error": "testing abort"}}')
    ss = st.create_session(url=stellar_addr)
    with pytest.raises(SessionError):
        ss.entity_resolution(StellarGraph('graph.epgm', 'test_er'), EntityResolution())
