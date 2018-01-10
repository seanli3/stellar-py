import stellar_py as st

STELLAR_ADDR = "http://localhost:3000"
ss = st.connect(STELLAR_ADDR)
ingestor = ss.create_ingestor(
    name = "test-graph",
    schema = {
        'vertex_classes': [
            st.VertexClass(
                name = "Person",
                properties = {
                    "name": "stringtype",
                    "dob": "datetype"
                }),
            st.VertexClass(
                name = "Location",
                properties = {
                    "address": "stringtype"
                })],
        'edge_classes': [
            st.EdgeClass(
                name = "Lives-At",
                src_class = "Person",
                dst_class = "Location",
                properties = {
                    "since": "datetype"
                }),
            st.EdgeClass(
                name = "Last-Messaged",
                src_class = "Person",
                dst_class = "Person",
                properties = {
                    "date": "datetype"
                })
        ]})

ingestor = ingestor.add_source(
        path = "people.csv",
        mapping = {
            "vertices": [
                st.VertexMapping(
                    vertex_class = "Person",
                    vertex_id = "PERSON_ID",
                    properties = {
                        "name": "NAME",
                        "dob": "DOB"
                    }
                )
            ]
        }
    ).add_source(
        path = "locations.csv",
        mapping = {
            "vertices": [
                st.VertexMapping(
                    vertex_class = "Location",
                    vertex_id = "LOCATION_ID",
                    properties = {
                        "address": "ADDR"
                    }
                )
            ]
        }
    ).add_source(
        path = "lives-at.csv",
        mapping = {
            "edges": [
                st.EdgeMapping(
                    edge_class = "Lives-At",
                    src_class = "Person",
                    src = "PERSON_ID",
                    dst = "LOCATION_ID",
                    properties = {
                        "since": "MOVE_IN_DATE"
                    }
                )
            ]
        }
    ).add_source(
        path = "last-msg.csv",
        mapping = {
            "edges": [
                st.EdgeMapping(
                    edge_class = "Last-Messaged",
                    src_class = "Person",
                    src = "FROM_ID",
                    dst = "TO_ID",
                    properties = {
                        "date": "DATE"
                    }
                )
            ]
        }
    )

ingestor.ingest()
