import stellar_py as st


ss = st.create_session(url="stlr://12.34.56.78", session_id="test")

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
graph_ingest = ss.run_ingestor(schema=schema, sources=data_sources).await_result()
# graph_ingest = ss.run_ingestor(payload=jsonPayload)

# entity resolution
# TODO
# graph_er = ss.run_entity_resolution(graph=graph_ingest, params={}).await_result()

# node embedder
# TODO
# embed_task = ss.run_embedder(graph=graph_er, target="local/path/to/embedded.csv", format="csv")

# node attr inference
# TODO
# nai_task = ss.run_nai(graph=graph_er, params={})

# check results
# result_embed = embed_task.get_result()
# result_nai = nai_task.get_result()
# graph_nai = result_nai.graph if result_nai.status == 'completed' else None

# write to path
# TODO
# result_write = ss.write_graph(graph=graph_nai, target="local/path/to/graph.epgm", format="json")

# if result_embed.success:
#     import pandas as pd
#     df = pd.read_csv("local/path/to/embedded.csv")
