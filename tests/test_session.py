from stellar.session import *
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
    assert repr(result) == 'StellarResult(status=completed,success=True,dir="graph.epgm",reason="")'


def test_result_fail():
    payload = {'error': 'session error'}
    result = StellarResult('aborted', payload)
    assert result.status == 'aborted'
    assert not result.success
    assert result.reason == 'session error'
    assert repr(result) == 'StellarResult(status=aborted,success=False,dir="",reason="session error")'


@pytest.fixture(scope='module')
def get_task():
    return StellarTask('12341234', 6379, 'ingest', '1234')


def test_task_repr():
    task = get_task()
    assert repr(task) == 'StellarTask(name="ingest",id="coordinator:sessions:1234")'


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


def test_task_wait_for_result_timeout(monkeypatch):
    monkeypatch.setattr(
        redis.StrictRedis,
        'get',
        lambda *_: u'{"status": "running", "ingest": {"output": "test_path.epgm", "error":""}}'
    )
    with pytest.raises(polling.TimeoutException):
        result = get_task().wait_for_result(timeout=0.1)


def test_session_repr():
    session = StellarSession('12.34.12.34', 3000)
    assert repr(session) == 'StellarSession(url="http://12.34.12.34:3000")'


@httpretty.activate
def test_session_init():
    session = StellarSession('12.34.12.34', 3000)
    session2 = StellarSession('localhost', 5000)
    assert session._url == 'http://12.34.12.34:3000'
    assert session._redis_url == '12.34.12.34'
    assert session._redis_port == 6379
    assert session2._url == 'http://localhost:5000'


@httpretty.activate
def test_session_get():
    httpretty.register_uri(httpretty.GET, 'http://12341234:5000/endpt', body=u'{"key": "value", "key2": "value2"}')
    session = StellarSession('12341234', 5000)
    response = session._get('endpt').json()
    assert response['key'] == 'value'
    assert response['key2'] == 'value2'


@httpretty.activate
def test_session_post():
    httpretty.register_uri(httpretty.POST, 'http://12341234:5000/endpt', body=u'{"key": "value", "key2": "value2"}')
    session = StellarSession('12341234', 5000)
    response = session._post('endpt', u'{"somekey": "someval"}').json()
    assert response['key'] == 'value'
    assert response['key2'] == 'value2'


@httpretty.activate
def test_get_session_id():
    httpretty.register_uri(httpretty.GET, 'http://12.12.12.12:8000/init', body=u'{"sessionId": "test_session"}')
    session = StellarSession('12.12.12.12', 8000)
    session_id = session._get_session_id()
    assert session_id == 'test_session'


@httpretty.activate
def test_get_session_id_empty_resp():
    httpretty.register_uri(httpretty.GET, 'http://12.12.12.12:8000/init', body="")
    session = StellarSession('12.12.12.12', 8000)
    with pytest.raises(SessionError):
        session._get_session_id()


@httpretty.activate
def test_get_session_id_key_error():
    httpretty.register_uri(httpretty.GET, 'http://12.12.12.12:8000/init', body=u'{"wrong":"answer"}')
    session = StellarSession('12.12.12.12', 8000)
    with pytest.raises(SessionError):
        session._get_session_id()


@httpretty.activate
def test_start():
    httpretty.register_uri(httpretty.GET, 'http://12.12.12.12:8000/init', body=u'{"sessionId":"test_session"}')
    httpretty.register_uri(httpretty.POST, 'http://12.12.12.12:8000/test_task/start')
    session = StellarSession('12.12.12.12', 8000)
    task = session._start('test_task', lambda sid: Payload(sid, "test_label"))
    assert task._session_id == 'coordinator:sessions:test_session'
    assert task._name == 'test_task'
