__copyright__ = """

    This file is part of stellar-py, Stellar Python Client.

    Copyright 2018 CSIRO Data61

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

"""
__license__ = "Apache 2.0"

from setuptools import setup
from setuptools import find_packages

setup(name='stellar-py',
      version='0.2.1',
      description='Python client for the Stellar project',
      url='https://github.com/data61/stellar-py',
      author='Kevin Jung',
      author_email='kevin.jung@data61.csiro.au',
      license='Apache 2.0',
      install_requires=['requests', 'redis', 'polling', 'networkx'],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      extras_require={
            'testing': ['httpretty', 'coveralls'],
      },
      packages=find_packages())
