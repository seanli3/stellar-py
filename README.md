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
    conda create --name stellar pip
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
import stellar as st

# create session
ss = st.create_session(url="stlr://12.34.56.78")

# create graph schema
schema = st.create_schema().add_node_type(
    name='Person',
    attribute_types={
        'first name': 'string',
        'last name': 'string',
        'age': 'integer'
    }
)

# configure data source
node_map = schema.node['Person'].create_map(
    path='people.csv',
    column='ID',
    map_attributes={
        'first name': 'FIRST_NAME',
        'last name': 'SURNAME',
        'age': 'AGE'
    }
)

# create graph 
graph = ss.ingest(schema=schema, mappings=[node_map], label='people')
```

## Other examples
Examples can be found [here](examples)

## Additional Documentation
Visit <https://data61.github.io/stellar-py> for a more in-depth guide and API references.
