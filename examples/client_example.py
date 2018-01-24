import stellar_py as st


ss = st.connect("stlr://12.34.56.78")

# config for different modules
ingestor_conf = {
    "task": "ingest",
    "graph_label": "ingest",
    "conf": {}
}
entity_resolution_conf = {
    "task": "er",
    "graph_label": "er",
    "conf": {}
}
nai_conf = {
    "task": "nai",
    "graph_label": "nai",
    "conf": {}
}
save_conf = {
    "task": "save",
    "conf": {
        "format": "json",
        "path": "local/path/to/graph.epgm"
    }
}

# make task plan and then request execution
result = ss.with_sources(ingestor_conf).then(entity_resolution_conf).then(nai_conf).then(save_conf).execute()

# reuse previously ingested graph for alternate task plan (different conf, different order)
er_conf_alt = {
    "task": "er",
    "graph_label": "er_alt",
    "conf": {
        "something": "here"
    }
}
nai_conf_alt = {
    "task": "nai",
    "graph_label": "nai_alt",
    "conf": {
        "something": "here"
    }
}
result_er_alt = ss.with_graph("ingest").then(nai_conf_alt).then(er_conf_alt).then(save_conf).execute()

# reusing graph labels raises exception to avoid duplicate labels
# this plan raises for duplicate label "nai" since a graph with that label already exists from previous tasks
result_nai_then_er = ss.with_graph("ingest").then(nai_conf).then(save_conf).execute()

# some outputs are not graphs (e.g. embedder)
embed_conf = {
    "task": "embed",
    "conf": {
        "path": "local/path/to/features.csv"
    }
}
result_embed = ss.with_graph("nai").then(embed_conf).execute()
if result_embed.success:
    import pandas as pd
    df = pd.read_csv("local/path/to/features.csv")
