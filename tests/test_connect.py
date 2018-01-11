import pytest
import stellar_py as st

def test_connect():
    addr = "http://localhost:3000"
    session_id = "stellar_session"
    ss = st.connect(addr)
    assert ss.addr == addr
    assert ss.session_id == "stellar_py_session"
    ss = st.connect(addr, session_id)
    assert ss.addr == addr
    assert ss.session_id == session_id
