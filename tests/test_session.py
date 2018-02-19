from stellar_py.session import *
import redis
import pytest
import httpretty


def test_session_error():
    with pytest.raises(SessionError):
        raise SessionError(500, "session error")


def test_result_success():
    payload = {'output': 'graph.epgm'}
    result = StellarResult('completed', payload)
    assert result.status == 'completed'
    assert result.success
    assert result.dir == 'graph.epgm'


def test_result_fail():
    payload = {'error': 'session error'}
    result = StellarResult('aborted', payload)
    assert result.status == 'aborted'
    assert not result.success
    assert result.reason == 'session error'


@pytest.fixture(scope='module')
def get_task():
    return StellarTask('12341234', 6379, 'ingest', 'test:sessions:1234')


def test_task_init(monkeypatch):
    monkeypatch.setattr(redis, 'StrictRedis',
                        lambda **kwargs: kwargs)
    task = get_task()
    assert task._r['host'] == '12341234'
    assert task._r['port'] == 6379
    assert task._r['db'] == 0
    assert task._r['decode_responses']


def test_task_check_status(monkeypatch):
    monkeypatch.setattr(
        redis.StrictRedis,
        'get',
        lambda *_: u'{"status": "completed", "ingest": {"output": "test_path.epgm", "error":""}}'
    )
    assert get_task().check_status() == 'completed'


def test_task_wait_for_result(monkeypatch):
    monkeypatch.setattr(
        redis.StrictRedis,
        'get',
        lambda *_: u'{"status": "completed", "ingest": {"output": "test_path.epgm", "error":""}}'
    )
    result = get_task().wait_for_result()
    assert result.success
    assert result.status == 'completed'
    assert result.dir == 'test_path.epgm'


@httpretty.activate
def test_session_init():
    httpretty.register_uri(httpretty.GET, 'http://12341234/init', body=u'{"sessionId": "new_sesh"}')
    session = StellarSession('http://12341234')
    assert session._session_id == 'new_sesh'
    assert session._url == 'http://12341234'
    assert session._redis_url == 'localhost'
    assert session._redis_port == 6379


@httpretty.activate
def test_session_init_server_error():
    httpretty.register_uri(httpretty.GET, 'http://12341234/init',
                           body=u'{"reason": "server error"}', status=500)
    with pytest.raises(SessionError):
        StellarSession('http://12341234')


@httpretty.activate
def test_session_get():
    httpretty.register_uri(httpretty.GET, 'http://12341234/init', body=u'{"sessionId": "new_sesh"}')
    httpretty.register_uri(httpretty.GET, 'http://12341234/endpt', body=u'{"key": "value", "key2": "value2"}')
    session = StellarSession('http://12341234')
    response = session._get('endpt').json()
    assert response['key'] == 'value'
    assert response['key2'] == 'value2'


@httpretty.activate
def test_session_post():
    httpretty.register_uri(httpretty.GET, 'http://12341234/init', body=u'{"sessionId": "new_sesh"}')
    httpretty.register_uri(httpretty.POST, 'http://12341234/endpt', body=u'{"key": "value", "key2": "value2"}')
    session = StellarSession('http://12341234')
    response = session._post('endpt', u'{"somekey": "someval"}').json()
    assert response['key'] == 'value'
    assert response['key2'] == 'value2'


@httpretty.activate
def test_session_get_task_update_session(monkeypatch):
    httpretty.register_uri(httpretty.GET, 'http://12341234/init', body=u'{"sessionId": "old_sesh"}')
    session = StellarSession('http://12341234')
    monkeypatch.setattr(redis, 'StrictRedis',
                        lambda **kwargs: kwargs)
    task = session._get_task_update_session('ingest', 'new_sesh')
    assert session._session_id == 'new_sesh'
    assert task._session_id == 'coordinator:sessions:old_sesh'
    assert task._r['host'] == 'localhost'
    assert task._r['port'] == 6379
