"""Test for NAI"""

from stellar_py.nai import *
from stellar_py.session import SessionError
import stellar_py as st
from redis import StrictRedis
import httpretty
import pytest


stellar_addr = "http://localhost:3000"
stellar_addr_nai = stellar_addr + "/nai/tasks"
stellar_addr_session = stellar_addr + "/session/create"


def test_nai_payload():
    graph = StellarGraph('graph.epgm', 'test_nai_ori')
    payload = StellarNAIPayload(session_id='test_session', graph=graph, target_attribute='target_attr',
                                node_type='type', attributes_to_ignore=['ignored_1', 'ignored_2'], label='test_nai')
    assert payload.sessionId == 'test_session'
    assert payload.input == 'graph.epgm'
    assert payload.inputs['in_data']['dataset_name'] == 'test_nai_ori'
    assert payload.parameters['target_attribute'] == 'target_attr'
    assert payload.parameters['node_type'] == 'type'
    assert payload.parameters['attributes_to_ignore'] == ['ignored_1', 'ignored_2']
    assert payload.label == 'test_nai'


@httpretty.activate
def test_nai_start():
    httpretty.register_uri(httpretty.POST, stellar_addr_nai,
                           body=u'{"sessionId": "melon"}')
    httpretty.register_uri(httpretty.GET, stellar_addr_session, body=u'{"sessionId": "dummy_session_id"}')
    ss = st.create_session(url=stellar_addr)
    task = ss.nai_start(StellarGraph('graph.epgm', 'test_nai_ori'), 'target_attr', 'type', [], 'test_nai')
    assert task._session_id == "stellar:coordinator:sessions:dummy_session_id"
    assert ss._session_id == "melon"


@httpretty.activate
def test_nai(monkeypatch):
    httpretty.register_uri(httpretty.POST, stellar_addr_nai, body=u'{"sessionId": "melon"}')
    httpretty.register_uri(httpretty.GET, stellar_addr_session, body=u'{"sessionId": "dummy_session_id"}')
    monkeypatch.setattr(
        'test_nai.StrictRedis.get',
        lambda *_: u'{"status": "completed", "nai": {"output": "test_path.epgm", "error":""}}')
    ss = st.create_session(url=stellar_addr)
    graph = ss.nai(StellarGraph('graph.epgm', 'test_nai_ori'), 'target_attr', 'type')
    assert graph.path == "test_path.epgm"
    assert graph.label == 'test_nai_ori'


@httpretty.activate
def test_nai_error(monkeypatch):
    httpretty.register_uri(httpretty.POST, stellar_addr_nai, body=u'{"sessionId": "melon"}')
    httpretty.register_uri(httpretty.GET, stellar_addr_session, body=u'{"sessionId": "dummy_session_id"}')
    monkeypatch.setattr(
        'test_nai.StrictRedis.get',
        lambda *_: u'{"status": "aborted", "nai": {"output": "", "error": "testing abort"}}')
    ss = st.create_session(url=stellar_addr)
    with pytest.raises(SessionError):
        ss.nai(StellarGraph('graph.epgm', 'test_nai_ori'), 'target_attr', 'type')
