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

    try:
        with open(filename, "wb") as registry_file:
            registry_file.write(yaml.dump(registry, default_flow_style=False))
    except:
        print "Failed to save registry file at %s." % filename


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

    try:
        with open(filename, "rb") as registry_file:
            parsed = yaml.load(registry_file.read())
    except:
        print "Failed to parse '%s' as YAML." % filename

    if parsed is None:
        raise Exception("An error occurred during parsing of YAML file at '%s'." % filename)
        
    return parsed
