import stellar as st
import networkx as nx


"""Create session"""
ss = st.create_session(url="http://localhost:8000")

"""Create graph schema"""
schema = st.create_schema()
schema.add_node_type(
    name='Person',
    attribute_types={
        'full_name': 'string',
        'address': 'string',
        'risk': 'string'
    }
)
schema.add_edge_type(
    name='Association',
    src_type='Person',
    dst_type='Person'
)

"""Create data source mappings"""
m_person = schema.node['Person'].create_map(
    path='/opt/stellar/data/risk_net/risk_net_names.csv',
    column='id',
    map_attributes={
        'full_name': 'name',
        'address': 'address',
        'risk': 'risk',
    }
)

m_assoc = schema.edge['Association'].create_map(
    path='/opt/stellar/data/risk_net/risk_net_associations.csv',
    src='person1',
    dst='person2'
)

mappings = [m_person, m_assoc]

"""Ingestor"""
graph_ingest = ss.ingest(schema=schema, mappings=mappings, label='risk_net')

"""Entity Resolution"""
graph_er = ss.entity_resolution(graph=graph_ingest, resolver=st.entity.EntityResolution())

"""Node Attribute Inference"""
graph_nai = ss.predict(
    graph=graph_ingest,
    model=st.model.Node2Vec(),
    target_attribute='risk',
    node_type='Person',
    attributes_to_ignore=['__id', 'full_name', 'address']
)

"""Load graph with networkx"""
graph_nx = graph_nai.to_networkx()

"""Write graph in GraphML format"""
nx.write_graphml(nx.DiGraph(graph_nx), "/opt/stellar/data/risk_net/risk_net.graphml")
