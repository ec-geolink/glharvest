"""registry.py

Functionality for working with the Harvest System's registry file.
"""

from os.path import isfile
import yaml

def save_registry(filename, registry):
    """Save the registry to disk.

    Arguments:
    ----------
    registry : Dict
    """

    with open(filename, "wb") as registry_file:
        registry_file.write(yaml.dump(registry, default_flow_style=False))


def parse_registry_file(filename):
    """Parse the registry file.

    Arguments:
    ----------

    filename : str
    """

    if not isfile(filename):
        print "Couldn't find specified file: `%s`." % filename
        return None


    parsed = None

    with open(filename, "rb") as registry_file:
        parsed = yaml.load(registry_file.read())

    return parsed
