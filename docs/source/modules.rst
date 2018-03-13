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

* The target node attribute to be predicted can be of any type, but is treated as categorical with the number of
  unique values defining the number of classes. The resulting predictive model for the target attribute is a classifier.
* Node attributes to be used as predictors for the target node attribute must be numeric (int or float) or convertible
  to numeric (strings like "0", "1", "3.14", etc.), otherwise they must be added to the list of attributes to ignore.
  See the documentation on the NAI plugin on how to specify node attributes to ignore.
* Predictors must have no missing values. The target node attribute to predict, on the other hand, can have missing
  values in the input data.
* The input dataset should include positive examples (support) for each class label of the target attribute.
* All NAI pipelines support homogeneous graph input (the graph only has a single node and edge type). A NAI pipeline
  using representation learning via node2vec does support heterogeneous graph as input as well, as long as the node
  type of interest (the type of nodes whose attributes are to be predicted) is explicitly specified by the user.


