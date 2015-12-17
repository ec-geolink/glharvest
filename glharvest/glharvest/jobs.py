"""jobs.py

Jobs for the Harvest System.
"""

import sys
import os
import requests
import urllib
import datetime
from dateutil.parser import parse
import RDF

from d1lod.sesame import Store, Repository
from glharvest import registry, void, util

# RQ
from redis import StrictRedis
from rq import Queue

conn = StrictRedis(host='redis', port='6379')
q = Queue(connection=conn)

SESAME_HOST = os.getenv('WEB_1_PORT_8080_TCP_ADDR', 'localhost')
SESAME_PORT = os.getenv('WEB_1_PORT_8080_TCP_PORT', '8080')
SESAME_REPOSITORY = 'glharvest'


def update():
    """Update the contents of the Harvester.

    Reads the registry file and does work depending on what it finds.
    """

    print "job.update()"
    print "Parsing registry file."

    # Establish the location of the registry file
    # The else case will run when not running in a container
    if os.path.isfile('/glharvest/registry.yml'):
        registry_filepath = '/glharvest/registry.yml'
    else:
        registry_filepath = 'registry.yml'

    if not os.path.isfile:
        print "Couldn't locate the registry file at the provided path: %s. Exiting." % registry_filepath
        return

    registry_file = registry.parse_registry_file(registry_filepath)

    if registry_file is None:
        print "Failed to parse registry file. Exiting."
        return

    print "Registry file parsed. %d provider(s) found." % len(registry_file)

    for provider in registry_file:
        # Validate and extract information for each provider
        print "Validating provider: %s." % provider

        # Check for VoID
        if 'void' not in registry_file[provider]:
            print "Location of VoID dataset not found for this provider in the registry. Skipping."
            continue

        voidfile = registry_file[provider]['void']

        # Check for modified value
        if 'modified' not in registry_file[provider]:
            print "Location of VoID dataset not found for this provider in the registry."
            registry_modified = None
        else:
            registry_modified = registry_file[provider]['modified']
            print registry_modified
            registry_modified = parse(str(registry_modified), ignoretz=True)

            print registry_modified
        print "Registry has a last modified value of %s." % registry_modified

        # Get and parse the VoID file
        print "Attemting to retrieve VoID file from location %s." % voidfile

        try:
            r = requests.get(voidfile)
        except:
            print "Failed to get voidfile located at `%s`." % voidfile
            continue

        void_string_format = "rdfxml"

        # Use another format is we detect a different one
        if voidfile.endswith('ttl'):
            void_string_format = 'turtle'

        print "Loading VoID file"
        model = util.load_string_into_model(r.text, fmt=void_string_format)
        void_model = void.parse_void_model(model)

        print void_model

        for provider_dataset in void_model:
            print "Processing provider VoID:Dataset %s." % provider_dataset

            if 'modified' not in void_model[provider_dataset]:
                print "VoID:Dataset found in VoID dump did not have dcterms:modified value. Skipping."
                continue

            if 'features' not in void_model[provider_dataset]:
                print "VoID:Dataset has no feature declaration. Skipping."
                continue

            modified = void_model[provider_dataset]['modified']

            try:
                modified = parse(modified, ignoretz=True)
            except:
                print "Failed to parse modified time string of %s. Skipping." % modified
                continue

            print "After parsing, `modified` value is %s." % modified

            # TODO process features
            features = void_model[provider_dataset]['features']
            print "Found features: %s" % features

            print "Updating dataset if %s is greater than %s." % (modified, registry_modified)

            if registry_modified is None or modified > registry_modified:
                print "Updating dataset %s." % provider_dataset

                # Set up repository connection
                s = Store(SESAME_HOST, SESAME_PORT)
                r = Repository(s, SESAME_REPOSITORY)

                data_dumps = void_model[provider_dataset]['dumps']

                for dump in data_dumps:
                    print "Processing %s %s %s." % (provider, provider_dataset, dump)

                    # Create a temporary name for the file
                    outfilename = datetime.datetime.now().strftime("%s-%f")

                    try:
                        # resp = requests.get(dump)
                        urllib.urlretrieve(dump, outfilename)
                    except:
                        print "Failed to fetch the void file at `%s`. Skipping." % dump
                        continue

                    # Decide the format (from looking at the URL string)
                    dump_file_format = "rdfxml"

                    # Use another format is we detect a different one
                    if dump.endswith('ttl'):
                        dump_file_format = 'turtle'

                    # parser = RDF.Parser(name=dump_file_format)

                    # Delete triples about each subject (streaming)
                    # for statement in parser.parse_as_stream('file:' + outfilename):
                    #     # Don't delete statements about non_URI subjects because
                    #     # we can't
                    #     if not statement.subject.is_resource():
                    #         continue
                    #
                    #     print "Deleting triples in context %s about %s." % (provider, str(statement.subject))
                    #     r.delete_triples_about(statement.subject, context=provider)

                    # Just delete all triples in the context
                    print "Deleting triples in context %s." % provider
                    r.delete_triples_about('?s', context=provider)

                    # Import the file
                    print "Importing temp file '%s' into named graph '%s'." % (outfilename, provider)
                    r.import_from_file(outfilename, context=provider, fmt=dump_file_format)

                    # Delete the temp file
                    os.remove(outfilename)


                # Update registry file on disk
                print "Updating registry with new modified datetime of %s." % modified
                registry_file[provider]['modified'] = modified
                registry.save_registry("registry.yml", registry_file)
            else:
                print "datadump has not been updated since the last visit. Doing nothing."


def export():
    """Export the repository as Turtle."""

    s = Store(SESAME_HOST, SESAME_PORT)
    r = Repository(s, SESAME_REPOSITORY)

    with open('/www/export.ttl', 'wb') as f:
        exported_text = r.export()
        f.write(exported_text.encode('utf-8'))


def status():
    """Gets the status of the system and prints to stdout."""
    print "Getting the status of the system."

    s = Store(SESAME_HOST, SESAME_PORT)
    r = Repository(s, SESAME_REPOSITORY)

    print "Repository size is %d" % r.size()
