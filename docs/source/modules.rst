Module Info
***********

This page contains information about what's currently configurable for each of the modules using the Python client, and
any relevant limitations.

Ingestion
=========

Requirements
------------
* Data sources must be in CSV format, containing headings as the first row.
* Each row in a data source must correspond to an `entry` in the graph - i.e. a node or an edge. Rows can be reused if
  each row is to be mapped to multiple entries, but multiple rows cannot be used to form a single entry.

Additional Info / Limitations
-----------------------------
* Failing to provide a correct path to an existing file source may sometimes result in the Python client hanging
  without a response.
* Including non-existing column names in the mappings will not produce errors in the ingestion, but will produce a
  graph that hasn't been mapped properly - i.e. the incorrectly-mapped attribute will be missing. If you incorrectly map
  the column corresponding to ID, the graph will not contain the proper entries.

Entity Resolution
=================

Configurations
--------------
* Currently there is one fixed set of configurations for Entity Resolution. Use an instance of
  ``stellar.entity.EntityResolution`` as the resolver when running the module.

Machine Learning Models
=======================

Configurations
--------------
Each configuration corresponds to a pipeline containing a set of plugins. Refer to the documentation for
`Stellar Evaluation Plugins <https://data61.github.io/stellar-evaluation-plugins/html/index.html>`_ for more
information about each of the plugins.

* ``stellar.model.Node2Vec`` - pipeline contains NAI Splitter, NAI Representation Learning, and NAI inference.
* ``stellar.model.Node2Vec(metric_learning=True)`` - Node2Vec pipeline + NAI Metric Learning
* ``stellar.model.GCN`` - pipeline contains NAI Splitter, and GCN

Additional configurations specific to each plugin within the pipeline may become available in the future.

Additional Info / Limitations
-----------------------------
* For any of the `Node2Vec` pipeline configurations, every node in the input graph must contain at least one outgoing
  edge. One possible approach to ensure this condition will always be satisfied, is to add a self-loop edge for every
  node when you initially create the graph.
* If the graph contains too few nodes/edges, the default configurations included with the installation may not work.
* The input graph must be homogeneous.


