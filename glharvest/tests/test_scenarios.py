"""test_scenarios.py

End-end-end tests for the Harvester.
"""

import sys
import os
import RDF

from glharvest import jobs, registry, void


def test_can_update_a_provider_with_a_new_resource(repository):
    """This test tests the case where a provider gives informationa about one
    resource at time t0 then, at time t1, their data dump no longer contains
    information about the old resource. In this case, we keep the previous
    knowledge and add the new knowledge because we don't allow providers to
    completely remove a resource.
    """

    # Setup
    repository.clear()
    provider = 'test'
    infile_fmt = 'turtle'
    base_uri = 'http://example.org/test/'
    parser = RDF.TurtleParser()

    state_t0 = """
    @prefix void: <http://rdfs.org/ns/void#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix test: <http://example.org/test/> .

    test:A a test:Thing ;
      test:someProperty 'some property' .
    """

    state_t1 = """@prefix void: <http://rdfs.org/ns/void#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix test: <http://example.org/test/> .

    test:B a test:Thing ;
      test:someProperty 'some other property' .
    """

    # State t0
    for statement in parser.parse_string_as_stream(state_t0, base_uri=base_uri):
        print statement.subject
        repository.delete_triples_about(statement.subject, context=provider)

    repository.import_from_string(state_t0, context=provider, fmt=infile_fmt)

    assert repository.size() == 2

    # State t1
    for statement in parser.parse_string_as_stream(state_t1, base_uri=base_uri):
        print statement.subject
        repository.delete_triples_about(statement.subject, context=provider)

    repository.import_from_string(state_t1, context=provider, fmt=infile_fmt)

    assert repository.size() == 4


def test_provide_can_change_knowledge_about_a_previous_resource(repository):
    """This test tests the case where a provider wishes to change the knowledge
    about a resource. They do this by making an update datadump with at least
    one statement about that resource.
    """

    # Setup
    repository.clear()
    provider = 'test'
    infile_fmt = 'turtle'
    base_uri = 'http://example.org/test/'
    parser = RDF.TurtleParser()

    state_t0 = """
    @prefix void: <http://rdfs.org/ns/void#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix test: <http://example.org/test/> .

    test:A a test:Thing ;
      test:someProperty 'some property' ;
      test:anotherProperty 'just another thing' .
    """

    state_t1 = """@prefix void: <http://rdfs.org/ns/void#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix test: <http://example.org/test/> .

    test:A a test:Thing ;
      test:someProperty 'some other property' .
    """

    # State t0
    for statement in parser.parse_string_as_stream(state_t0, base_uri=base_uri):
        repository.delete_triples_about(statement.subject, context=provider)

    repository.import_from_string(state_t0, context=provider, fmt=infile_fmt)

    assert repository.size() == 3

    # State t1
    for statement in parser.parse_string_as_stream(state_t1, base_uri=base_uri):
        repository.delete_triples_about(statement.subject, context=provider)

    assert repository.size() == 0

    repository.import_from_string(state_t1, context=provider, fmt=infile_fmt)

    assert repository.size() == 2


def test_can_handle_multiple_duplicate_updates(repository):
    """This tests the case where a provider's datadump is updated but contains
    the same information as the datadump at a previous time. We'd assume the
    result would be that all statements would be first removed then just added
    again so the size would go from N to 0 back to N.
    """

    # Setup
    repository.clear()
    provider = 'test'
    infile_fmt = 'turtle'
    base_uri = 'http://example.org/test/'
    parser = RDF.TurtleParser()

    state_t0 = """
    @prefix void: <http://rdfs.org/ns/void#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix test: <http://example.org/test/> .

    test:A a test:Thing ;
      test:someProperty 'some property' ;
      test:anotherProperty 'just another thing' .
    """

    state_t1 = """
    @prefix void: <http://rdfs.org/ns/void#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix test: <http://example.org/test/> .

    test:A a test:Thing ;
      test:someProperty 'some property' ;
      test:anotherProperty 'just another thing' .
    """

    # State t0
    for statement in parser.parse_string_as_stream(state_t0, base_uri=base_uri):
        repository.delete_triples_about(statement.subject, context=provider)

    repository.import_from_string(state_t0, context=provider, fmt=infile_fmt)

    assert repository.size() == 3

    # State t1
    for statement in parser.parse_string_as_stream(state_t1, base_uri=base_uri):
        repository.delete_triples_about(statement.subject, context=provider)

    assert repository.size() == 0

    repository.import_from_string(state_t1, context=provider, fmt=infile_fmt)

    assert repository.size() == 3


def test_can_handle_multiple_providers(repository):
    """This test tests the case where there are two registered providers. Each
    provider should have triples in their respective named graph.
    """

    # Setup
    repository.clear()
    infile_fmt = 'turtle'
    base_uri = 'http://example.org/test/'
    parser = RDF.TurtleParser()

    state_t0 = """
    @prefix void: <http://rdfs.org/ns/void#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix test: <http://example.org/test/> .

    test:A a test:Thing ;
      test:someProperty 'some property' ;
      test:anotherProperty 'just another thing' .
    """

    state_t1 = """
    @prefix void: <http://rdfs.org/ns/void#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix test: <http://example.org/test/> .

    test:A a test:Thing ;
      test:someProperty 'some property' ;
      test:anotherProperty 'just another thing' .
    """

    # State t0
    provider = 'providerA'
    for statement in parser.parse_string_as_stream(state_t0, base_uri=base_uri):
        repository.delete_triples_about(statement.subject, context=provider)

    repository.import_from_string(state_t0, context=provider, fmt=infile_fmt)

    assert repository.size() == 3

    # State t1
    provider = 'providerB'
    for statement in parser.parse_string_as_stream(state_t1, base_uri=base_uri):
        repository.delete_triples_about(statement.subject, context=provider)

    assert repository.size() == 3

    repository.import_from_string(state_t1, context=provider, fmt=infile_fmt)

    assert repository.size() == 6
