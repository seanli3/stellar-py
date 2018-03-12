# stellar-py

|Branch|Build|Coverage|
|:-----|:----:|:----:|
|*master*|[![Build Status](https://travis-ci.org/data61/stellar-py.svg?branch=master)](https://travis-ci.org/data61/stellar-py)|[![Coverage Status](https://coveralls.io/repos/github/data61/stellar-py/badge.svg?branch=master)](https://coveralls.io/github/data61/stellar-py?branch=master)|
|*devel*|[![Build Status](https://travis-ci.org/data61/stellar-py.svg?branch=devel)](https://travis-ci.org/data61/stellar-py)|[![Coverage Status](https://coveralls.io/repos/github/data61/stellar-py/badge.svg?branch=devel)](https://coveralls.io/github/data61/stellar-py?branch=devel)|

## Introduction

This repository hosts stellar-py, the Python Client for the [Stellar Graph Analytics](https://github.com/data61/stellar) platform developed by [CSIRO Data61](https://data61.csiro.au).

The Stellar Python Client can perform the following functions:
 * Connect to the main Stellar platform
 * Ingest data from a CSV into a graph format
 * Perform entity resolution on the graph
 * Run a machine learning model to predict node attributes
 * Convert a graph into a networkx object

If you are interested in running the entire Stellar platform, please refer to the instructions on the main Stellar [repository](https://github.com/data61/stellar).

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

## License
Copyright 2018 CSIRO Data61

Licensed under  the Apache License, Version  2.0 (the "License"); you  may not
use  the files  included  in this  repository except  in  compliance with  the
License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless  required  by  applicable  law   or  agreed  to  in  writing,  software
distributed under  the License  is distributed  on an  "AS IS"  BASIS, WITHOUT
WARRANTIES OR  CONDITIONS OF  ANY KIND,  either express  or implied.   See the
License for the specific language  governing permissions and limitations under
the License.

