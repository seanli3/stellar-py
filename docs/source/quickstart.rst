Quickstart
**********

Requirements
============

Environment Setup
-----------------
Ensure you have completed the procedure in :doc:`installation` to have your python environment set up correctly.
Refer to the main `Stellar repository <https://github.com/data61/stellar>`_ to setup all other Stellar modules.

Example Dataset
---------------
With the recommended installation and setup, datasets should be placed in the directory "/opt/stellar/data".
Your Stellar installation should come with an example dataset called `risk_net` which contains two CSV data sources -
"risk_net/names.csv" and "risk_net/associations.csv".

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

Mappings
========
Mappings are used to define how column names of a csv data source correspond to attributes of the graph's nodes and
edges. The schema we defined earlier contains a dictionary of the different types of nodes and edges we created.
Each of them contain a method ``create_map``, which can be used to create a mapping for that particular node/edge type.
We can map column names in our dataset to our `Person` node and `Association` edge using the syntax below::

    m_person = schema.node['Person'].create_map(
        path='risk_net/names.csv',
        column='ID',
        map_attributes={
            'full_name': 'FULLNAME',
            'address': 'ADDR',
            'risk': 'RISK'
        }
    )
    m_assoc = schema.edge['Association'].create_map(
        path='risk_net/associations.csv',
        src='SRC',
        dst='DST'
    )

Ingestion
=========
Use the schema and list of mappings we've created to create a graph. The label is a string to identify the graph::

    graph = ss.ingest(schema=schema, mappings=[m_person, m_assoc], label='risk_net')

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
        target_attribute='risk',
        node_type='Person',
        attributes_to_ignore=[
            '__id',
            'full_name',
            'address'
        ]
    )

Write to GraphML
================
GraphML is a popular XML based file format for storing graphs, which is often supported by other applications,
e.g. Gephi - a graph visualisation tool.::

    graph.to_graphml(path='/opt/stellar/data/risk_net/risk_net.graphml')

Networkx
========
The graph object contains a method called ``to_networkx`` that can be used to load the graph as a
``networkx.MultiDiGraph`` object. Since Networkx only supports homogeneous graphs, the `type` information of nodes/edges
must either be omitted or you can use an optional parameter ``inc_type_as`` to include it as an additional attribute.::

    nx_graph = graph.to_networkx(inc_type_as='_type')

Complete Example
================

.. literalinclude:: ../../examples/risk_net.py
