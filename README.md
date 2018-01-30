# stellar-py [![Build Status](https://travis-ci.org/data61/stellar-py.svg?branch=devel)](https://travis-ci.org/data61/stellar-py)
Python client for the Stellar Project

## Requirements
Creating and setting up an environment to use `stellar-py` using Anaconda:
1. Download and install Anaconda 3 from <http://continuum.io>
2. Create a Conda environment. The following command creates an environment called `stellar` and installs `pip`.
    ```
    conda create -name stellar pip
    ```
3. Activate the new environment.
    ```
    source activate stellar
    ```
4. Install `stellar-py` using `pip`.
    ```
    pip install git+git://github.com/data61/stellar-py
    ``` 
You can also skip straight to `4.` if you would like to install in an existing environment.

## Basic Usage
Ingest from a single data source with columns (ID, FIRST_NAME, SURNAME, AGE) as vertices
```python
import stellar_py as st

# create session
ss = st.create_session(url="stlr://12.34.56.78")

# create graph schema
schema = st.create_graph_schema()
schema.add_vertex_class(
    name='Person',
    properties={
        'first name': 'string',
        'last name': 'string',
        'age': 'integer'
    }
)

# configure data source
data_source = st.new_data_source(path='people.csv')
data_source.add_vertex_mapping(
    schema.vertex['Person'].create_mapping(
        vertex_id='ID',
        properties={
            'first name': 'FIRST_NAME',
            'last name': 'SURNAME',
            'age': 'AGE'
        }
    )
)

# run ingestor
task = ss.run_ingestor(schema=schema, sources=[data_source])
result = task.wait_for_result()
```
