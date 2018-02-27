from stellar_py.ingestion import *
from redis import StrictRedis
import stellar_py as st
import pytest
import httpretty

stellar_addr = "http://localhost:3000"
stellar_addr_ingest = stellar_addr + "/ingest/start"
stellar_addr_session = stellar_addr + "/init"


@pytest.fixture(scope="module")
def graph_schema():
    schema = create_graph_schema()
    schema.add_vertex_class(name='src vertex')
    schema.add_vertex_class(name='dst vertex', properties={})
    schema.add_vertex_class(name='dst vertex 2', properties={'number': 'integer'})
    schema.add_edge_class(name='edge', src_class='src vertex', dst_class='dst vertex')
    schema.add_edge_class(name='edge 2', src_class='src vertex', dst_class='dst vertex 2',
                          properties={'str': 'string'})
    return schema


@pytest.fixture(scope="module")
def data_source():
    schema = graph_schema()
    source = new_data_source("path")
    source.add_vertex_mapping(schema.vertex['src vertex'].create_mapping(vertex_id="SrcId"))
    source.add_vertex_mapping(schema.vertex['dst vertex'].create_mapping(vertex_id="DstId",
                                                                         properties={}))
    source.add_vertex_mapping(schema.vertex['dst vertex 2'].create_mapping(
        vertex_id="DstId2", properties={'number': 'Number'}))
    source.add_edge_mapping(schema.edge['edge'].create_mapping(src="SrcId", dst="DstId"))
    source.add_edge_mapping(schema.edge['edge 2'].create_mapping(src="SrcId", dst="DstId2",
                                                                 properties={'str': 'Address'}))
    return source


def test_graph_schema():
    schema = graph_schema()
    assert schema.vertex['src vertex'].name == 'src vertex'
    assert schema.vertex['src vertex'].properties == {}
    assert schema.vertex['dst vertex'].name == 'dst vertex'
    assert schema.vertex['dst vertex'].properties == {}
    assert schema.vertex['dst vertex 2'].name == 'dst vertex 2'
    assert schema.vertex['dst vertex 2'].properties == {'number': 'integer'}
    assert schema.edge['edge'].name == 'edge'
    assert schema.edge['edge'].src_class == 'src vertex'
    assert schema.edge['edge'].dst_class == 'dst vertex'
    assert schema.edge['edge'].properties == {}
    assert schema.edge['edge 2'].name == 'edge 2'
    assert schema.edge['edge 2'].src_class == 'src vertex'
    assert schema.edge['edge 2'].dst_class == 'dst vertex 2'
    assert schema.edge['edge 2'].properties == {'str': 'string'}


def test_data_source():
    source = data_source()
    assert source.path == "path"
    assert len(source.vertex_mappings) == 3
    assert len(source.edge_mappings) == 2


def test_data_source_invalid_properties():
    schema = graph_schema()
    source = new_data_source("path")
    with pytest.raises(KeyError):
        source.add_vertex_mapping(
            schema.vertex['src vertex'].create_mapping(vertex_id="SrcId", properties={'number': 'Number'}))
    with pytest.raises(KeyError):
        source.add_edge_mapping(schema.edge['edge 2'].create_mapping(src='SrcId', dst='DstId2',
                                                                     properties={'str_bad': 'Address'}))


def test_ingest_payload():
    schema = graph_schema()
    source = data_source()
    payload = StellarIngestPayload(session_id="id", schema=schema, sources=[source], label="test_ingest_payload")
    assert payload.sessionId == "id"
    assert payload.sources == ['path']
    assert payload.label == 'test_ingest_payload'
    assert len(payload.graphSchema['classes']) == len(schema.vertex)
    assert len(payload.graphSchema['classLinks']) == len(schema.edge)
    assert len(payload.mapping['nodes']) == len(source.vertex_mappings)
    assert len(payload.mapping['links']) == len(source.edge_mappings)


def test_ingest_payload_vc2c():
    vc = graph_schema().vertex['dst vertex 2']
    c = StellarIngestPayload.vc2c(vc)
    assert vc.name == c['name']
    assert vc.properties == c['props']
    vc_noprops = graph_schema().vertex['src vertex']
    c_noprops = StellarIngestPayload.vc2c(vc_noprops)
    assert vc_noprops.name == c_noprops['name']
    assert c_noprops['props'] == {}


def test_ingest_payload_ec2cl():
    ec = graph_schema().edge['edge 2']
    cl = StellarIngestPayload.ec2cl(ec)
    assert ec.name == cl['name']
    assert ec.properties == cl['props']
    ec_noprops = graph_schema().edge['edge']
    cl_noprops = StellarIngestPayload.ec2cl(ec_noprops)
    assert ec_noprops.name == cl_noprops['name']
    assert cl_noprops['props'] == {}


def test_ingest_payload_vms2nodes():
    src = new_data_source('path')
    src.add_vertex_mapping(graph_schema().vertex['dst vertex 2'].create_mapping(vertex_id='Id',
                                                                                properties={'number': 'Number'}))
    nodes = StellarIngestPayload.vms2nodes('path', src.vertex_mappings)
    assert nodes[0]['@id'] == {'column': 'Id', 'source': 'path'}
    assert nodes[0]['@type'] == 'dst vertex 2'
    assert nodes[0]['number'] == {'column': 'Number', 'source': 'path'}


def test_ingest_payload_ems2links():
    src = new_data_source('path')
    src.add_edge_mapping(graph_schema().edge['edge 2'].create_mapping(src='SrcId',
                                                                      dst='DstId',
                                                                      properties={'str': 'Address'}))
    links = StellarIngestPayload.ems2links('path', src.edge_mappings)
    assert links[0]['@src'] == {'column': 'SrcId', 'source': 'path'}
    assert links[0]['@dest'] == {'column': 'DstId', 'source': 'path'}
    assert links[0]['@type'] == {'name': 'edge 2', 'source': 'src vertex'}
    assert links[0]['str'] == {'column': 'Address', 'source': 'path'}


@httpretty.activate
def test_ingest_start():
    httpretty.register_uri(httpretty.POST, stellar_addr_ingest)
    httpretty.register_uri(httpretty.GET, stellar_addr_session, body=u'{"sessionId": "dummy_session_id"}')
    ss = st.create_session(url=stellar_addr)
    task = ss.ingest_start(graph_schema(), [data_source()], 'test_ingest')
    assert task._session_id == "coordinator:sessions:dummy_session_id"


@httpretty.activate
def test_ingest(monkeypatch):
    httpretty.register_uri(httpretty.POST, stellar_addr_ingest, body=u'{"sessionId": "melon"}')
    httpretty.register_uri(httpretty.GET, stellar_addr_session, body=u'{"sessionId": "dummy_session_id"}')
    monkeypatch.setattr(
        'test_ingestion.StrictRedis.get',
        lambda *_: u'{"status": "completed", "ingest": {"output": "test_path.epgm", "error":""}}')
    ss = st.create_session(url=stellar_addr)
    graph = ss.ingest(graph_schema(), [data_source()], 'test_ingest')
    assert graph.path == "test_path.epgm"
