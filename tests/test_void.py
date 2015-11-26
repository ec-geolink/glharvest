"""test_void.py

Test the parsing of VoID dump files.

"""

import RDF

from glharvest import util

def test_can_load_a_simple_void_file():
    model = util.load_file_into_model('tests/data/simple-void.ttl', 'turtle')
    p = util.parse_void_model(model)

    assert p == {   'http://lod.dataone.org/test': {
                        'dataDump': 'http://lod.dataone.org/test.ttl',
                        'features': [
                            'http://lod.dataone.org/fulldump'
                        ]
                    }
                }
