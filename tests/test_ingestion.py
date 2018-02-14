from stellar_py.ingestion import *
from redis import StrictRedis
import stellar_py as st
import pytest
import httpretty

stellar_addr = "http://localhost:3000"
stellar_addr_ingest = stellar_addr + "/ingestor/start"
stellar_addr_session = stellar_addr + "/session/create"


@pytest.fixture(scope="module")
def graph_schema():
    schema = create_graph_schema()
    schema.add_node_type(name='src node')
    schema.add_node_type(name='dst node', attribute_types={})
    schema.add_node_type(name='dst node 2', attribute_types={'number': 'integer'})
    schema.add_edge_type(name='edge', src_type='src node', dst_type='dst node')
    schema.add_edge_type(name='edge 2', src_type='src node', dst_type='dst node 2',
                         attribute_types={'str': 'string'})
    return schema


@pytest.fixture(scope="module")
def data_source():
    schema = graph_schema()
    source = new_data_source("path")
    source.add_node_mapping(schema.node['src node'].create_mapping(node_id="SrcId"))
    source.add_node_mapping(schema.node['dst node'].create_mapping(node_id="DstId",
                                                                     attributes={}))
    source.add_node_mapping(schema.node['dst node 2'].create_mapping(
        node_id="DstId2", attributes={'number': 'Number'}))
    source.add_edge_mapping(schema.edge['edge'].create_mapping(src="SrcId", dst="DstId"))
    source.add_edge_mapping(schema.edge['edge 2'].create_mapping(src="SrcId", dst="DstId2",
                                                                 attributes={'str': 'Address'}))
    return source


def test_graph_schema():
    schema = graph_schema()
    assert schema.node['src node'].name == 'src node'
    assert schema.node['src node'].attribute_types == {}
    assert schema.node['dst node'].name == 'dst node'
    assert schema.node['dst node'].attribute_types == {}
    assert schema.node['dst node 2'].name == 'dst node 2'
    assert schema.node['dst node 2'].attribute_types == {'number': 'integer'}
    assert schema.edge['edge'].name == 'edge'
    assert schema.edge['edge'].src_type == 'src node'
    assert schema.edge['edge'].dst_type == 'dst node'
    assert schema.edge['edge'].attribute_types == {}
    assert schema.edge['edge 2'].name == 'edge 2'
    assert schema.edge['edge 2'].src_type == 'src node'
    assert schema.edge['edge 2'].dst_type == 'dst node 2'
    assert schema.edge['edge 2'].attribute_types == {'str': 'string'}


def test_data_source():
    source = data_source()
    assert source.path == "path"
    assert len(source.node_mappings) == 3
    assert len(source.edge_mappings) == 2


def test_data_source_invalid_properties():
    schema = graph_schema()
    source = new_data_source("path")
    with pytest.raises(KeyError):
        source.add_node_mapping(
            schema.node['src node'].create_mapping(node_id="SrcId", attributes={'number': 'Number'}))
    with pytest.raises(KeyError):
        source.add_edge_mapping(schema.edge['edge 2'].create_mapping(src='SrcId', dst='DstId2',
                                                                     attributes={'str_bad': 'Address'}))


def test_ingest_payload():
    schema = graph_schema()
    source = data_source()
    payload = StellarIngestPayload(session_id="id", schema=schema, sources=[source], label="test_ingest_payload")
    assert payload.sessionId == "id"
    assert payload.sources == ['path']
    assert payload.label == 'test_ingest_payload'
    assert len(payload.graphSchema['classes']) == len(schema.node)
    assert len(payload.graphSchema['classLinks']) == len(schema.edge)
    assert len(payload.mapping['nodes']) == len(source.node_mappings)
    assert len(payload.mapping['links']) == len(source.edge_mappings)


def test_ingest_payload_vc2c():
    vc = graph_schema().node['dst node 2']
    c = StellarIngestPayload.nt2c(vc)
    assert vc.name == c['name']
    assert vc.attribute_types == c['props']
    vc_noprops = graph_schema().node['src node']
    c_noprops = StellarIngestPayload.nt2c(vc_noprops)
    assert vc_noprops.name == c_noprops['name']
    assert c_noprops['props'] == {}


def test_ingest_payload_ec2cl():
    ec = graph_schema().edge['edge 2']
    cl = StellarIngestPayload.et2cl(ec)
    assert ec.name == cl['name']
    assert ec.attribute_types == cl['props']
    ec_noprops = graph_schema().edge['edge']
    cl_noprops = StellarIngestPayload.et2cl(ec_noprops)
    assert ec_noprops.name == cl_noprops['name']
    assert cl_noprops['props'] == {}


def test_ingest_payload_vms2nodes():
    src = new_data_source('path')
    src.add_node_mapping(graph_schema().node['dst node 2'].create_mapping(node_id='Id',
                                                                            attributes={'number': 'Number'}))
    nodes = StellarIngestPayload.nms2nodes('path', src.node_mappings)
    assert nodes[0]['@id'] == {'column': 'Id', 'source': 'path'}
    assert nodes[0]['@type'] == 'dst node 2'
    assert nodes[0]['number'] == {'column': 'Number', 'source': 'path'}


def test_ingest_payload_ems2links():
    src = new_data_source('path')
    src.add_edge_mapping(graph_schema().edge['edge 2'].create_mapping(src='SrcId',
                                                                      dst='DstId',
                                                                      attributes={'str': 'Address'}))
    links = StellarIngestPayload.ems2links('path', src.edge_mappings)
    assert links[0]['@src'] == {'column': 'SrcId', 'source': 'path'}
    assert links[0]['@dest'] == {'column': 'DstId', 'source': 'path'}
    assert links[0]['@type'] == {'name': 'edge 2', 'source': 'src node'}
    assert links[0]['str'] == {'column': 'Address', 'source': 'path'}


@httpretty.activate
def test_ingest_start():
    httpretty.register_uri(httpretty.POST, stellar_addr_ingest,
                           body=u'{"sessionId": "melon"}')
    httpretty.register_uri(httpretty.GET, stellar_addr_session, body=u'{"sessionId": "dummy_session_id"}')
    ss = st.create_session(url=stellar_addr)
    task = ss.ingest_start(graph_schema(), [data_source()], 'test_ingest')
    assert task._session_id == "stellar:coordinator:sessions:dummy_session_id"
    assert ss._session_id == "melon"


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
