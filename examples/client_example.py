import stellar as st
import networkx as nx


"""Create session"""
ss = st.create_session(url="http://localhost:3000")

"""Create graph schema"""
schema = st.create_schema()
schema.add_node_type(
    name='Paper',
    attribute_types={
        'dataset': 'string',
        'title': 'string',
        'venue': 'string',
        'year': 'integer'
    }
)
schema.add_edge_type(
    name='SharesAuthor',
    src_type='Paper',
    dst_type='Paper',
    attribute_types={
        'author': 'string'
    }
)

"""Create data source mappings"""
paper_nodes = schema.node['Paper'].create_map(
    path='papers.csv',
    column='Id',
    map_attributes={
        'dataset': 'dataset',
        'title': 'title',
        'venue': 'venue',
        'year': 'year'
    }
)

selfauth_edges = schema.edge['SharesAuthor'].create_map(
    path='papers.csv',
    src='Id',
    dst='Id',
    map_attributes={
        'author': 'Id'
    }
)

auth_edges = schema.edge['SharesAuthor'].create_map(
    path='authors.csv',
    src='Source',
    dst='Target',
    map_attributes={
        'author': 'Author'
    }
)

mappings = [paper_nodes, selfauth_edges, auth_edges]

"""Ingestor"""
graph_ingest = ss.ingest(schema=schema, mappings=mappings, label='papers')

"""Entity Resolution"""
graph_er = ss.entity_resolution(graph=graph_ingest, resolver=st.entity.EntityResolution())

"""Node Attribute Inference"""
graph_nai = ss.predict(
    graph=graph_er,
    model=st.model.Node2Vec(),
    target_attribute='venue',
    node_type='Paper',
    attributes_to_ignore=['__id', 'title', 'dataset']
)

"""Load graph with networkx"""
graph_nx = graph_nai.to_networkx()

"""Write graph in GraphML format"""
nx.write_graphml(nx.DiGraph(graph_nx), "papers.graphml")
