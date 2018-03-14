.. stellar-py documentation master file, created by
   sphinx-quickstart on Mon Feb 26 17:55:25 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Stellar Python Client
*********************

Welcome to Stellar Python Client's documentation, the Python Client for the
`Stellar Graph Analytics <https://github.com/data61/stellar>`_ platform developed by
`CSIRO Data61 <https://data61.csiro.au>`_.

The Stellar Python Client can perform the following functions:

* Connect to the main Stellar platform
* Ingest data from a CSV into a graph format
* Perform entity resolution the graph
* Run a machine learning model to predict node attributes
* Convert a graph into a networkx object

If you are interested in running the entire Stellar platform, please refer to the instructions on the main Stellar
`repository <https://github.com/data61/stellar>`_.

Once you have your Stellar platform up and running, refer to :doc:`installation` to setup your environment for the
Python client, and then to :doc:`quickstart` for a quick tutorial on how to create and analyse a graph using the
example dataset. For a more in-depth look into the library, please refer to the API references and the official
`GitHub repository <https://github.com/data61/stellar-py>`_.

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   modules

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   session
   graph

.. toctree::
   :maxdepth: 2
   :caption: Additional Notes

   changelog
   license
