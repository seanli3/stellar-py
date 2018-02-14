# stellar-py 
Python client for the Stellar Project

|Branch|Build|Coverage|
|:-----|:----:|:----:|
|*master*|[![Build Status](https://travis-ci.org/data61/stellar-py.svg?branch=master)](https://travis-ci.org/data61/stellar-py)|[![Coverage Status](https://coveralls.io/repos/github/data61/stellar-py/badge.svg?branch=master)](https://coveralls.io/github/data61/stellar-py?branch=master)|
|*devel*|[![Build Status](https://travis-ci.org/data61/stellar-py.svg?branch=devel)](https://travis-ci.org/data61/stellar-py)|[![Coverage Status](https://coveralls.io/repos/github/data61/stellar-py/badge.svg?branch=devel)](https://coveralls.io/github/data61/stellar-py?branch=devel)|

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
schema.add_node_type(
    name='Person',
    attribute_types={
        'first name': 'string',
        'last name': 'string',
        'age': 'integer'
    }
)

# configure data source
data_source = st.new_data_source(path='people.csv')
data_source.add_node_mapping(
    schema.node['Person'].create_mapping(
        node_id='ID',
        attributes={
            'first name': 'FIRST_NAME',
            'last name': 'SURNAME',
            'age': 'AGE'
        }
    )
)

# run ingestor
graph_ingest = ss.ingest(schema=schema, sources=[data_source])
```

## Other examples
Examples can be found [here](examples)
