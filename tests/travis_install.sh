#!/bin/bash
# This script is meant to be called by the "install" step defined in
# .travis.yml. See http://docs.travis-ci.com/ for more details.
# The behavior of the script is controlled by environment variabled defined
# in the .travis.yml in the top level folder of the project.
#
# This script is adapted from Scikit-Learn (http://scikit-learn.org/)

set -e

# Deactivate the travis-provided virtual environment and setup a
# conda-based environment instead
deactivate

# Use the miniconda installer for faster download / install of conda
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    -O miniconda.sh
chmod +x miniconda.sh && ./miniconda.sh -b -p $HOME/miniconda
export PATH=$HOME/miniconda/bin:$PATH
# Don't ask for confirmation
conda config --set always_yes true
# Update conda
conda update conda

# Follow channel priority strictly
conda config --set channel_priority strict
# Don't change prompt
conda config --set changeps1 false

# Add conda-forge as priority channel
conda config --add channels conda-forge

# Configure the conda environment using package names (using .environment.yml would force
# the python version)
conda create -n testenv \
    python=$PYTHON_VERSION \
    fiona \
    geopandas \
    haversine \
    imageio \
    matplotlib \
    numpy \
    palettable \
    pandas \
    pyproj \
    pytest \
    pytest-cov \
    scipy

source activate testenv

pip install coverage coveralls

# Link code to python environment
# install any packages as specified in install_requires
python setup.py develop
