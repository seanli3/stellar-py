Installation
************

Python Virtual Environment
==========================

Using virtualenv
----------------

Install virtualenv::

    sudo apt-get install virtualenv

Navigate a project directory of your choice and create a Python 3 virtual environment::

    mkdir myproject
    cd myproject
    virtualenv -p python3 myproject-env

Activate the new virtual environment::

    . myproject-env/bin/activate


Using Anaconda
--------------

Download and install Anaconda 3 from http://continuum.io

Create a Conda environment and install pip::

    conda create -name myproject-env pip

Activate the new virtual environment::

    source activate myproject-env

Installing stellar-py
=====================

Make sure you have a python virtual environment activated - the name of your virtual environment should be visible on the prompt of your shell. Then you can install stellar-py with git.::

    sudo apt-get install git
    pip install git+git://github.com/data61/stellar-py



