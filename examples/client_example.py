import stellar_py as st


ss = st.create_session(url="http://localhost")

# create graph schema
schema = st.create_graph_schema()
schema.add_vertex_class(
    name='Author',
    properties={
        'extref_id': 'string',
        'type': 'string',
        'name': 'string'
    }
)
schema.add_edge_class(
    name='IsSameAs',
    src_class='Author',
    dst_class='Author'
)

# use schema to configure data sources
data_sources = list()
data_sources.append(
    st.new_data_source(path='nodes.csv').add_vertex_mapping(
        schema.vertex['Author'].create_mapping(
            vertex_id='Id',
            properties={
                'extref_id': 'Extref_Id',
                'type': 'Type',
                'name': 'Label'
            }
        )
    )
)
data_sources.append(
    st.new_data_source(path="edges.csv").add_edge_mapping(
        schema.edge['IsSameAs'].create_mapping(
            src="Source",
            dst="Target"
        )
    )
)

# ingestor
graph_ingest = ss.ingest(schema=schema, sources=data_sources, label='imdb')
# task_ingest = ss.ingest_start(schema=schema, sources=data_sources)
# graph_ingest = ss.ingest(payload=jsonPayload)

# entity resolution
# TODO
graph_er = ss.er(graph=graph_ingest, params={}, label='imdb_er')

# node embedder
# TODO
df = ss.embedder(graph=graph_er)

# node attr inference
# TODO
graph_nai = ss.nai(graph=graph_er, params={}, label='imdb_nai')

# graph to networkx
# TODO
graph_nx = ss.to_networkx(graph_nai)

