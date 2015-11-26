"""util.py
"""

import RDF
import yaml

from os.path import isfile


def load_file_into_model(filename, format="rdfxml"):
    """Load a file containing RDF into a Model.

    Arguments:
    ----------
    filename : str

        A relative (to script execution) filepath for a file.

    format : str

        One of:
            - rdfxml
            - turtle
            - Others: See http://librdf.org/raptor/

    Returns:
    --------
    RDF.Model or None if an exception occurred
    """

    try:
        storage = RDF.MemoryStorage()
    except:
        print "Failed to create RDF.Storage"
        return None

    try:
        model = RDF.Model(storage)
    except:
        print "Failed to create RDF.Model."
        return None

    try:
        parser = RDF.Parser(name=format)
    except:
        print "Failed to create RDF.Parser."
        return None

    file_uri = "file:./%s" % filename

    try:
        parser.parse_into_model(model, file_uri)
    except:
        print "Failed to parse %s into RDF.Model" % file_uri
        return None

    return model


def parse_void_model(model):
    """Parses a VoID document conatined in an RDF.Model into a Python Dict.

    Arguments:
    ----------
    model : RDF.Model

    Returns:
    --------
    Dict
    """

    if not isinstance(model, RDF.Model):
        print "'model' argument was not an RDF.Model. Returning."
        return None

    datasets = {}

    rdf = RDF.NS('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    void = RDF.NS('http://rdfs.org/ns/void#')
    dcterms = RDF.NS('http://purl.org/dc/terms/')

    # Find datasets
    dataset_pattern = RDF.Statement(subject=None, predicate=rdf['type'], object=void['Dataset'])

    for statement in model.find_statements(dataset_pattern):
        if not statement.subject.is_resource():
            continue

        subject_string = str(statement.subject)

        if subject_string in datasets:
            continue

        datasets[subject_string] = {}

    print datasets

    # Find features
    feature_pattern = RDF.Statement(subject=None, predicate=void['feature'], object=None)

    for statement in model.find_statements(feature_pattern):
        subject_string = str(statement.subject)

        if subject_string not in datasets:
            continue

        if 'features' not in datasets[subject_string]:
            datasets[subject_string]['features'] = []

        object_string = str(statement.object)

        if object_string not in datasets[subject_string]['features']:
            datasets[subject_string]['features'].append(object_string)


    # Find last modified
    modified_pattern = RDF.Statement(subject=None, predicate=dcterms['modified'], object=None)

    for statement in model.find_statements(modified_pattern):
        if str(statement.subject) not in datasets:
            continue

        object_string = str(statement.object)
        datasets[str(statement.subject)]['modified'] = object_string

    # Find dataDump
    datadump_pattern = RDF.Statement(subject=None, predicate=void['dataDump'], object=None)

    for statement in model.find_statements(datadump_pattern):
        subject_string = str(statement.subject)

        if subject_string not in datasets:
            continue

        if not statement.object.is_resource():
            print "Skipping"
            continue

        if str(statement.subject) not in datasets:
            print "skipping"
            continue

        object_string = str(statement.object)
        datasets[subject_string]['dataDump'] = object_string


    return datasets


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


if __name__ == "__main__":
    print 'hi'
