"""test_registry.py

Test code related to managing the registry.
"""

from datetime import date
from glharvest import util


def test_can_read_a_simple_registry_file():
    rf = util.parse_registry_file("tests/data/simple-registry.yml")

    assert rf == { 'd1lod': {
                    'dump': 'http://lod.dataone.org',
                    'features': [
                        'full',
                        'partial'
                    ],
                    'modified': date(2015, 10, 12)
                    }
                }
