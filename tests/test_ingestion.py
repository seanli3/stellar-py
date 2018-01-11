import stellar_py as st
import json
import pytest

stellar_addr = "http://localhost:3000"
graph_name = "test-graph"

testdata = [] # list of tuples of (schema, list of source mappings, expected payload)
testdata.append(
        (None, None, {
            "sessionId": "stellar_py_session",
            "sources": [],
            "graphSchema": {
                    "classes": [],
                    "classLinks": []
                },
            "mapping": {
                    "nodes": [],
                    "links": []
                }
            }))
testdata.append(
        ({
            'vertex_classes': [
                st.VertexClass(
                    name = "Person",
                    properties = {
                        "name": "string",
                        "dob": "datetype"
                    }),
                st.VertexClass(
                    name = "Location",
                    properties = {
                        "address": "string"
                    })
            ],
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
            ]
        },
        [
            {
                "path": "people.csv",
                "mapping": {
                    "vertices": [
                        st.VertexMapping(
                            vertex_class = "Person",
                            vertex_id = "NAME",
                            properties = {
                                "name": "NAME",
                                "dob": "DOB"
                            })
                    ]
                }
            },
            {
                "path": "locations.csv",
                "mapping": {
                    "vertices": [
                        st.VertexMapping(
                            vertex_class = "Location",
                            vertex_id = "ID",
                            properties = {
                                "address": "ADDRESS"
                            })
                    ]
                }
            },
            {
                "path": "lives-at.csv",
                "mapping": {
                    "edges": [
                        st.EdgeMapping(
                            edge_class = "Lives-At",
                            src_class = "Person",
                            src = "NAME",
                            dst = "LOCATION",
                            properties = {
                                "since": "MOVE-IN DATE"
                            })
                    ]
                }
            },
            {
                "path": "last-msg.csv",
                "mapping": {
                    "edges": [
                        st.EdgeMapping(
                            edge_class = "Last-Messaged",
                            src_class = "Person",
                            src = "NAME",
                            dst = "LAST-MESSAGED",
                            properties = {
                                "date": "MESSAGE DATE"
                            })
                    ]
                }
            }
        ],
        {
            "sessionId": "stellar_py_session",
            "sources": [
                "people.csv",
                "locations.csv",
                "lives-at.csv",
                "last-msg.csv"
            ],
            "graphSchema": {
                "classes": [
                    {
                        "name": "Person",
                        "props": {
                            "name": "string",
                            "dob": "datetype"
                        }
                    },
                    {
                        "name": "Location",
                        "props": {
                            "address": "string"
                        }
                    }
                ],
                "classLinks": [
                    {
                        "name": "Lives-At",
                        "source": "Person",
                        "target": "Location",
                        "props": {
                            "since": "datetype"
                        }
                    },
                    {
                        "name": "Last-Messaged",
                        "source": "Person",
                        "target": "Person",
                        "props": {
                            "date": "datetype"
                        }
                    }
                ]
            },
            "mapping": {
                "nodes": [
                    {
                        "@id": {
                            "column": "NAME",
                            "source": "people.csv"
                        },
                        "@type": "Person",
                        "name": {
                            "column": "NAME",
                            "source": "people.csv"
                        },
                        "dob" : {
                            "column": "DOB",
                            "source": "people.csv"
                        }
                    },
                    {
                        "@id": {
                            "column": "ID",
                            "source": "locations.csv"
                        },
                        "@type": "Location",
                        "address": {
                            "column": "ADDRESS",
                            "source": "locations.csv"
                        }
                    }
                ],
                "links": [
                    {
                        "@src": {
                            "column": "NAME",
                            "source": "lives-at.csv"
                        },
                        "@dest": {
                            "column": "LOCATION",
                            "source": "lives-at.csv"
                        },
                        "@type": {
                            "name": "Lives-At",
                            "source": "Person"
                        },
                        "since": {
                            "column": "MOVE-IN DATE",
                            "source": "lives-at.csv"
                        }
                    },
                    {
                        "@src": {
                            "column": "NAME",
                            "source": "last-msg.csv"
                        },
                        "@dest": {
                            "column": "LAST-MESSAGED",
                            "source": "last-msg.csv"
                        },
                        "@type": {
                            "name": "Last-Messaged",
                            "source": "Person"
                        },
                        "date": {
                            "column": "MESSAGE DATE",
                            "source": "last-msg.csv"
                        }
                    }
                ]
            }
        }))

@pytest.mark.parametrize("schema,sources,expected", testdata, ids=["empty", "friends&addr"])
def test_ingestor_payload(schema, sources, expected, monkeypatch):
    ss = st.connect(stellar_addr)
    ing = ss.create_ingestor(name=graph_name, schema=schema)
    sources = [] if sources is None else sources
    for source in sources:
        ing = ing.add_source(path=source["path"], mapping=source["mapping"])
    assert ing.get_payload().__dict__ == expected
