"""test_util.py

Test functions located in the util module.
"""

import RDF

from glharvest import util

def test_can_load_a_file_into_a_model():
    parsed = util.load_file_into_model("void-dataset.ttl", "turtle")

    assert isinstance(parsed, RDF.Model)

def test_cant_load_a_file_into_a_model_of_the_wrong_foramt():
    parsed = util.load_file_into_model("void-dataset.ttl")

    assert parsed is None
