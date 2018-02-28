import stellar_py as st
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
papers = st.new_data_source(path='papers.csv')
papers.add_node_mapping(schema.node['Paper'].create_map(
    node_id='Id',
    attributes={
        'dataset': 'dataset',
        'title': 'title',
        'venue': 'venue',
        'year': 'year'
    }
))
papers.add_edge_mapping(schema.edge['SharesAuthor'].create_map(
    src='Id',
    dst='Id',
    attributes={
        'author': 'Id'
    }
))
authlinks = st.new_data_source(path='paperlinks.csv')
authlinks.add_edge_mapping(schema.edge['SharesAuthor'].create_map(
    src='Source',
    dst='Target',
    attributes={
        'author': 'Author'
    }
))
data_sources = [papers, authlinks]

"""Ingestor"""
graph_ingest = ss.ingest(schema=schema, sources=data_sources, label='papers')

"""Entity Resolution"""
graph_er = ss.er(graph=graph_ingest)

"""Node Attribute Inference"""
graph_nai = ss.nai(
    graph=graph_er,
    target_attribute='venue',
    node_type='Paper',
    attributes_to_ignore=['__id', 'title', 'dataset']
)

"""Load graph with networkx"""
graph_nx = graph_nai.to_networkx()

"""Write graph in GraphML format"""
nx.write_graphml(nx.DiGraph(graph_nx), "papers.graphml")
