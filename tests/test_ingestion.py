import stellar_py as st
import pytest

stellar_addr = "http://localhost:3000"
graph_name = "test-graph"


@pytest.fixture(scope="module")
def graph_schema():
    schema = st.create_graph_schema()
    schema.add_vertex_class(name='src vertex')
    schema.add_vertex_class(name='dst vertex', properties={})
    schema.add_vertex_class(name='dst vertex 2', properties={'number': 'integer'})
    schema.add_edge_class(name='edge', src_class='src vertex', dst_class='dst vertex')
    schema.add_edge_class(name='edge 2', src_class='src vertex', dst_class='dst vertex 2',
                          properties={'str': 'string'})
    return schema


def test_graph_schema():
    schema = graph_schema()
    assert schema.vc['src vertex'].name == 'src vertex'
    assert schema.vc['src vertex'].properties == {}
    assert schema.vc['dst vertex'].name == 'dst vertex'
    assert schema.vc['dst vertex'].properties == {}
    assert schema.vc['dst vertex 2'].name == 'dst vertex 2'
    assert schema.vc['dst vertex 2'].properties == {'number': 'integer'}
    assert schema.ec['edge'].name == 'edge'
    assert schema.ec['edge'].src_class == 'src vertex'
    assert schema.ec['edge'].dst_class == 'dst vertex'
    assert schema.ec['edge'].properties == {}
    assert schema.ec['edge 2'].name == 'edge 2'
    assert schema.ec['edge 2'].src_class == 'src vertex'
    assert schema.ec['edge 2'].dst_class == 'dst vertex 2'
    assert schema.ec['edge 2'].properties == {'str': 'string'}


def test_data_source():
    schema = graph_schema()
    data_source = st.new_data_source("path")
    data_source = data_source.add_vertex_mapping(schema.vc['src vertex'].create_mapping(vertex_id="SrcId"))
    data_source = data_source.add_vertex_mapping(schema.vc['dst vertex'].create_mapping(vertex_id="DstId",
                                                                                        properties={}))
    data_source = data_source.add_vertex_mapping(schema.vc['dst vertex 2'].create_mapping(
        vertex_id="DstId2", properties={'number': 'Number'}))
    data_source = data_source.add_edge_mapping(schema.ec['edge'].create_mapping(src="SrcId", dst="DstId"))
    data_source = data_source.add_edge_mapping(schema.ec['edge 2'].create_mapping(src="SrcId", dst="DstId2",
                                                                                  properties={'str': 'Address'}))
    assert data_source.path == "path"
    assert len(data_source.vertex_mappings) == 3
    assert len(data_source.edge_mappings) == 2


def test_data_source_invalid_properties():
    schema = graph_schema()
    data_source = st.new_data_source("path")
    with pytest.raises(KeyError):
        data_source.add_vertex_mapping(
            schema.vc['src vertex'].create_mapping(vertex_id="SrcId", properties={'number': 'Number'}))
    with pytest.raises(KeyError):
        data_source.add_edge_mapping(schema.ec['edge 2'].create_mapping(src='SrcId', dst='DstId2',
                                                                        properties={'strr': 'Address'}))


