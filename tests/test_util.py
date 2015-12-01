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

def test_can_load_a_string_into_a_model():
	turtle = """
	@base <http://example.org/> .
	@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
	@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
	@prefix foaf: <http://xmlns.com/foaf/0.1/> .
	@prefix rel: <http://www.perceive.net/schemas/relationship/> .

	<#green-goblin>
	    rel:enemyOf <#spiderman> ;
	    a foaf:Person ;    # in the context of the Marvel universe
	    foaf:name "Green Goblin" .

	<#spiderman>
	    rel:enemyOf <#green-goblin> ;
	    a foaf:Person ;
	    foaf:name "Spiderman" .
	"""


	parsed = util.load_string_into_model(turtle, format="turtle")

	assert parsed is not None

def test_cant_load_a_bogus_string_into_a_model():
	turtle = """
	bogus ttl content
	"""


	parsed = util.load_string_into_model(turtle, format="turtle")

	assert parsed is None