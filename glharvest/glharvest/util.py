"""util.py
"""

import RDF

from os.path import isfile

def create_empty_model():
    """Creates an empty RDF Model using MemoryStorage.

    Returns:
    --------
    RDF.Model
    """

    # Create the Storage
    try:
        storage = RDF.MemoryStorage()
    except:
        print "Failed to create RDF.Storage"
        return None

    # Create the Model using the above Storage
    try:
        model = RDF.Model(storage)
    except:
        print "Failed to create RDF.Model."
        return None

    return model


def load_string_into_model(rdfstring, fmt="rdfxml"):
    """Load a remote file into an RDF Model

    Arguments:
    ----------
    rdfstring : str
        HTTP URI of a file

    fmt : str

        One of:
            - rdfxml
            - turtle
            - Others: See http://librdf.org/raptor/

     Returns:
    --------
    RDF.Model or None if an exception occurred
    """
    # Create an empty Model
    model = create_empty_model()

    # Create a Parser
    try:
        parser = RDF.Parser(name=fmt)
    except:
        print "Failed to create RDF.Parser."
        return None

    # Parse the string into the model
    try:
        parser.parse_string_into_model(model, rdfstring, "example.org")
    except:
        print "Failed to parse %s into RDF.Model" % rdfstring
        return None

    return model


def load_file_into_model(filename, fmt="rdfxml"):
    """Load a file containing RDF into a Model.

    Arguments:
    ----------
    filename : str

        A relative (to script execution) filepath for a file.

    fmt : str

        One of:
            - rdfxml
            - turtle
            - Others: See http://librdf.org/raptor/

    Returns:
    --------
    RDF.Model or None if an exception occurred
    """

    # Create an empty Model
    model = create_empty_model()

    # Create a Parser
    try:
        parser = RDF.Parser(name=fmt)
    except:
        print "Failed to create RDF.Parser."
        return None

    # Create a file: URI for the filename to load
    file_uri = "file:./%s" % filename

    # Parse the file into the Model
    try:
        parser.parse_into_model(model, file_uri)
    except:
        print "Failed to parse %s into RDF.Model" % file_uri
        return None

    return model
