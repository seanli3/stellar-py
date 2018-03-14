"""Papers Example"""

__copyright__ = """

    This file is part of stellar-py, Stellar Python Client.

    Copyright 2018 CSIRO Data61

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

"""
__license__ = "Apache 2.0"

import stellar as st
import networkx as nx


"""Create session"""
ss = st.create_session(url="http://localhost:8000")

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
