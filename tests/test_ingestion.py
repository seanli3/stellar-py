from stellar.ingestion import *
from redis import StrictRedis
import stellar as st
import pytest
import httpretty

stellar_addr = "http://localhost:3000"
stellar_addr_ingest = stellar_addr + "/ingest/start"
stellar_addr_session = stellar_addr + "/init"


@pytest.fixture(scope="module")
def graph_schema():
    schema = create_schema()
    schema.add_node_type(name='src node')
    schema.add_node_type(name='dst node', attribute_types={})
    schema.add_node_type(name='dst node 2', attribute_types={'number': 'integer'})
    schema.add_edge_type(name='edge', src_type='src node', dst_type='dst node')
    schema.add_edge_type(name='edge 2', src_type='src node', dst_type='dst node 2',
                         attribute_types={'str': 'string'})
    return schema


@pytest.fixture(scope="module")
def graph_mappings():
    schema = graph_schema()
    return [
        schema.node['src node'].create_map(path='path', column='SrcId'),
        schema.node['dst node'].create_map(path='path', column='DstId', map_attributes={}),
        schema.node['dst node 2'].create_map(path='path', column='DstId2',
                                             map_attributes={'number': 'Number'}),
        schema.edge['edge'].create_map(path='path', src='SrcId', dst='DstId'),
        schema.edge['edge 2'].create_map(path='path', src='SrcId', dst='DstId2',
                                         map_attributes={'str': 'Address'})
    ]


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


def test_create_node_map():
    schema = graph_schema()
    srcnode_map = schema.node['src node'].create_map(path='path', column='SrcId')
    dstnode_map = schema.node['dst node'].create_map(path='path', column='DstId', map_attributes={})
    dstnode2_map = schema.node['dst node 2'].create_map(path='path', column='DstId2',
                                                        map_attributes={'number': 'Number'})
    assert srcnode_map.node_type == 'src node'
    assert srcnode_map.path == 'path'
    assert srcnode_map.node_id == 'SrcId'
    assert srcnode_map.attributes == {}
    assert dstnode_map.attributes == {}
    assert dstnode2_map.attributes == {'number': 'Number'}


def test_create_edge_map():
    schema = graph_schema()
    edge_map = schema.edge['edge'].create_map(path='path', src='SrcId', dst='DstId')
    edge2_map = schema.edge['edge 2'].create_map(path='path', src='SrcId', dst='DstId2',
                                                 map_attributes={'str': 'Address'})
    assert edge_map.edge_type == 'edge'
    assert edge_map.src_type == 'src node'
    assert edge_map.path == 'path'
    assert edge_map.src == 'SrcId'
    assert edge_map.dst == 'DstId'
    assert edge_map.attributes == {}
    assert edge2_map.edge_type == 'edge 2'
    assert edge2_map.dst == 'DstId2'
    assert edge2_map.attributes == {'str': 'Address'}


def test_create_map_invalid_properties():
    schema = graph_schema()
    with pytest.raises(KeyError):
        schema.node['src node'].create_map(path='path', column='SrcId', map_attributes={'number': 'Number'})
    with pytest.raises(KeyError):
        schema.edge['edge 2'].create_map(path='path', src='SrcId', dst='DstId2', map_attributes={'str_bad': 'Address'})


def test_ingest_payload():
    schema = graph_schema()
    mappings = graph_mappings()
    payload = StellarIngestPayload(session_id="id", schema=schema, mappings=mappings, label="test_ingest_payload")
    assert payload.sessionId == "id"
    assert payload.sources == ['path']
    assert payload.label == 'test_ingest_payload'
    assert len(payload.graphSchema['classes']) == len(schema.node)
    assert len(payload.graphSchema['classLinks']) == len(schema.edge)
    assert len(payload.mapping['nodes']) == sum([1 for m in mappings if isinstance(m, NodeMapping)])
    assert len(payload.mapping['links']) == sum([1 for m in mappings if isinstance(m, EdgeMapping)])


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


def test_ingest_payload_vm2node():
    schema = graph_schema()
    dstnode2 = schema.node['dst node 2'].create_map(path='path', column='Id', map_attributes={'number': 'Number'})
    node = StellarIngestPayload.nm2node(dstnode2)
    assert node['@id'] == {'column': 'Id', 'source': 'path'}
    assert node['@type'] == 'dst node 2'
    assert node['number'] == {'column': 'Number', 'source': 'path'}


def test_ingest_payload_em2link():
    edge = graph_schema().edge['edge 2'].create_map(path='path', src='SrcId', dst='DstId',
                                                    map_attributes={'str': 'Address'})
    link = StellarIngestPayload.em2link(edge)
    assert link['@src'] == {'column': 'SrcId', 'source': 'path'}
    assert link['@dest'] == {'column': 'DstId', 'source': 'path'}
    assert link['@type'] == {'name': 'edge 2', 'source': 'src node'}
    assert link['str'] == {'column': 'Address', 'source': 'path'}


@httpretty.activate
def test_ingest_start():
    httpretty.register_uri(httpretty.POST, stellar_addr_ingest)
    httpretty.register_uri(httpretty.GET, stellar_addr_session, body=u'{"sessionId": "dummy_session_id"}')
    ss = st.create_session(url=stellar_addr)
    task = ss.ingest_start(graph_schema(), graph_mappings(), 'test_ingest')
    assert task._session_id == "coordinator:sessions:dummy_session_id"


@httpretty.activate
def test_ingest(monkeypatch):
    httpretty.register_uri(httpretty.POST, stellar_addr_ingest, body=u'{"sessionId": "melon"}')
    httpretty.register_uri(httpretty.GET, stellar_addr_session, body=u'{"sessionId": "dummy_session_id"}')
    monkeypatch.setattr(
        'test_ingestion.StrictRedis.get',
        lambda *_: u'{"status": "completed", "ingest": {"output": "test_path.epgm", "error":""}}')
    ss = st.create_session(url=stellar_addr)
    graph = ss.ingest(graph_schema(), graph_mappings(), 'test_ingest')
    assert graph.path == "test_path.epgm"
