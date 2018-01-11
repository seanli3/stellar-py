from setuptools import setup
from setuptools import find_packages

setup(name='stellar-py',
        version='0.0.1',
        description='Python client for the Stellar project',
        url='serene.sh',
        author='Kevin Jung',
        author_email='kevin.jung@data61.csiro.au',
        license='Apache 2.0',
        setup_requires=['pytest-runner'],
        tests_require=['pytest'],
        packages=find_packages())