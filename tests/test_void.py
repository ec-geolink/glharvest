"""test_void.py

Test the parsing of VoID dump files.

"""

import RDF

from glharvest import util


def test_returns_none_if_the_registry_file_is_not_found():
    m = util.load_file_into_model("nonexistantvoidfile.ttl")

    assert m is None


def test_can_load_a_simple_void_file():
    model = util.load_file_into_model('tests/data/simple-void.ttl', 'turtle')
    p = void.parse_void_model(m)

    assert p == {   'http://lod.dataone.org/test': {
                        'dataDump': 'http://lod.dataone.org/test.ttl',
                        'features': [
                            'http://lod.dataone.org/fulldump'
                        ]
                    }
                }
