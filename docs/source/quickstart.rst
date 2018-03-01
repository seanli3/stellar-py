Quickstart
**********

Requirements
============

Environment Setup
-----------------
Ensure you have completed the procedure in :doc:`installation` to have your python environment set up correctly.
Refer to [somewhere] to setup all other Stellar modules.

Example Dataset
---------------
Download the example dataset to use with this guide: [papers.csv, authors.csv].
Place them in a directory that can be read by the python client.

Jupyter Notebook
----------------
Running the examples in this guide will most likely be easiest using a Jupyter Notebook.
You can run individual cells and view their outputs, change parameters and run them again, etc.
Install Jupyter Notebook using pip::

    pip install jupyter notebook

If you followed the installation steps using Conda,
using Conda's Jupyter notebook extensions makes it easier to manage Conda environments within Jupyter Notebook::

    conda install nb_conda

You can fire up a notebook using the command::

    jupyter notebook

Create Session
==============

Import the module and create a session pointing to localhost at port 8000.::

    import stellar as st

    ss = st.create_session(url='localhost', port=8000)

Graph Schema
============
The graph schema defines the structure of the graph.
This requires defining for every type of:

- node: its name and its attribute types (if any)

- edge: its name, source node type, destination node type, and its attribute types (if any)

The syntax is as follows::

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

Mappings
========
Mappings are used to define how column names of a csv data source correspond to attributes of the graph's nodes and
edges. The schema we defined earlier contains a dictionary of the different types of nodes and edges we created.
Each of them contain a method ``create_map``, which can be used to create a mapping for that particular node/edge type.
We can map column names in our dataset to our ``Paper`` node and ``SharesAuthor`` edge using the syntax below::

    m_papers = schema.node['Paper'].create_map(
        path='/tmp/stellar/user/papers.csv',
        column='ID',
        map_attributes={
            'dataset': 'DATASET',
            'title': 'TITLE',
            'venue': 'VENUE',
            'year': 'YEAR'
        }
    )
    m_auth = schema.edge['SharesAuthor'].create_map(
        path='/tmp/stellar/user/authors.csv',
        src='SRC',
        dst='DST',
        map_attributes={
            'author': 'NAME'
        }
    )

Ingestion
=========
Use the schema and list of mappings we've created to create a graph. The label is a string to identify the graph::

    graph = ss.ingest(schema=schema, mappings=[m_papers, m_auth], label='papers')

Once you have a graph, you can use this graph object as input to other functions such as Entity Resolution and Node
Attribute Inference.
Entity Resolution
=================
Currently there is one fixed configuration for running the entity resolution module, which can be obtained through
creating an instance of the class ``stellar.entity.EntityResolution``::

    graph_resolved = ss.entity_resolution(graph=graph, resolver=st.model.EntityResolution())

Node Attribute Inference
========================
There are three pipeline configurations you can use for predicting node attributes. The basic configuration is used by
the model ``stellar.model.Node2Vec``. More information about the different pipelines can be found [here]. You also need
to specify which target attribute to predict, which node type to use, and which attributes to ignore.::

    graph_predicted = ss.predict(
        graph=graph,
        model=st.model.Node2Vec(),
        target_attribute='venue',
        node_type='Paper',
        attributes_to_ignore=[
            '__id',
            'dataset',
            'title'
        ]
    )

Write to GraphML
================
GraphML is a popular XML based file format for storing graphs, which is often supported by other applications,
e.g. Gephi - a graph visualisation tool.::

    graph.to_graphml(path='/tmp/stellar/user/mygraph.graphml')

Networkx
========
The graph object contains a method called ``to_networkx`` that can be used to load the graph as a
``networkx.MultiDiGraph`` object. Since Networkx only supports homogeneous graphs, the `type` information of nodes/edges
must either be omitted or you can use an optional parameter ``inc_type_as`` to include it as an additional attribute.::

    nx_graph = graph.to_networkx(inc_type_as='_type')

Complete Example
================

.. literalinclude:: ../../examples/client_example.py
