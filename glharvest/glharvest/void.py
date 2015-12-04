"""void.py

Functionality related to workign with VoID files.
"""

try:
    import RDF
except ImportError:
    import sys
    sys.path.append('/usr/lib/python2.7/dist-packages/')

import RDF


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
        subject_string = str(statement.subject)

        if subject_string in datasets:
            continue

        datasets[subject_string] = {}

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
            print "Skipping"
            continue

        if 'dumps' not in datasets[subject_string]:
            datasets[subject_string]['dumps'] = []

        object_string = str(statement.object)
        datasets[subject_string]['dumps'].append(object_string)


    return datasets
