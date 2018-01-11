import stellar_py as st
import pytest

testdata = [
        ("http://localhost:3000", "http://localhost:3000"),
        ("stlr://10.10.10.10", "stlr://10.10.10.10")
        ]
stellar_addr = "http://localhost:3000"

graph_name = "test-graph"
graph_schema = {
        'vertex_classes': [
            st.VertexClass(
                name = "Person",
                properties = [
                    ("name", "string"),
                    ("dob", "datetype")
                ]),
            st.VertexClass(
                name = "Location",
                properties = [
                    ("address", "string")
                ])
        ],
        'edge_classes': [
            st.EdgeClass(
                name = "Lives-at",
                src_class = "Person",
                dst_class = "Location",
                properties = [
                        ("since", "datetype")
                ]),
            st.EdgeClass(
                name = "Last-messaged",
                src_class = "Person",
                dst_class = "Person",
                properties = [
                    ("date", "datetype")
                ])
        ]
    }

@pytest.fixture(scope="module")
def session(request):
    return st.connect(getattr(request.module, "stellar_addr", "http://localhost:3001"))

@pytest.fixture(scope="function")
def ingestor(session, request):
    return session.create_ingestor(
            name=getattr(request.module, "graph_name", "test-graph"),
            schema=getattr(request.module, "graph_schema", {}))

def test_connect(session):
    assert session.addr == stellar_addr

def test_create_ingestor(ingestor):
    assert ingestor.name == graph_name
    assert ingestor.schema == graph_schema
    assert ingestor.sources == []
