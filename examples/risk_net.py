"""Risk Network Example"""

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
