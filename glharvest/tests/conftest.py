import pytest
import os
import sys
# Add local copy of d1lod to path
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir, 'd1lod'))

from glharvest import util
from d1lod.sesame import Store, Repository

@pytest.fixture(scope="module")
def store():
    return Store('localhost', 8080)

@pytest.fixture(scope="module")
def repository(store):
    return Repository(store, 'test')
