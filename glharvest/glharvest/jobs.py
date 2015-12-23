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
import logging

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

    JOB_NAME = "UPDATE"
    logging.info("[%s] Job started.", JOB_NAME)

    # Set up repository connection
    store = Store(SESAME_HOST, SESAME_PORT)
    repository = Repository(store, SESAME_REPOSITORY)

    # Establish the location of the registry file
    # The else case will run when not running in a container
    if os.path.isfile('/glharvest/registry.yml'):
        registry_filepath = '/glharvest/registry.yml'
    else:
        registry_filepath = 'registry.yml'

    logging.info("[%s] Loading registry file from location '%s'.", JOB_NAME, registry_filepath)

    if not os.path.isfile:
        raise Exception("Couldn't locate the registry file at the provided path: %s. Exiting.", registry_filepath)

    registry_file = registry.parse_registry_file(registry_filepath)
    logging.info("[%s] Registry file parsed. %d provider(s) found.", JOB_NAME, len(registry_file))

    for provider in registry_file:
        logging.info("[%s] Processing provider '%s'.", JOB_NAME, provider)

        # Check for VoID
        if 'void' not in registry_file[provider]:
            logging.error("[%s] Location of VoID dataset not found for this provider in the registry. Skipping.", JOB_NAME)
            continue

        voidfile = registry_file[provider]['void']

        # Check for modified value
        if 'modified' not in registry_file[provider]:
            logging.info("[%s] Modified date(time) was not found in the registry for provider '%s'. This will force harvesting for this provider.", JOB_NAME, provider)
            registry_modified = None
        else:
            registry_modified = registry_file[provider]['modified']
            registry_modified = parse(str(registry_modified), ignoretz=True)

        logging.info("[%s] Provider '%s' was last modified at '%s'.", JOB_NAME, provider, registry_modified)

        # Get and parse the VoID file
        logging.info("[%s] Attemting to retrieve VoID file from location %s.", JOB_NAME, voidfile)

        try:
            r = requests.get(voidfile)
        except:
            logging.error("[%s] Failed to get voidfile located at `%s`. Skipping.", JOB_NAME, voidfile)
            continue

        void_string_format = "rdfxml"

        # Use another format is we detect a different one
        if voidfile.endswith('ttl'):
            void_string_format = 'turtle'

        model = util.load_string_into_model(r.text, fmt=void_string_format)
        void_model = void.parse_void_model(model)

        for provider_dataset in void_model:
            logging.info("[%s] Processing provider VoID:Dataset '%s'.", JOB_NAME, provider_dataset)

            if 'modified' not in void_model[provider_dataset]:
                logging.error("[%s] VoID:Dataset found in VoID dump did not have dcterms:modified value. Skipping.", JOB_NAME)
                continue

            if 'features' not in void_model[provider_dataset]:
                logging.error("[%s] VoID:Dataset has no feature declaration. Skipping.", JOB_NAME)
                continue

            modified = void_model[provider_dataset]['modified']

            try:
                modified = parse(modified, ignoretz=True)
            except:
                logging.error("[%s] Failed to parse modified time string of %s. Skipping.", JOB_NAME, modified)
                continue

            # TODO process features
            features = void_model[provider_dataset]['features']
            logging.info("[%s] Found features: %s", JOB_NAME, features)


            if registry_modified is not None and modified <= registry_modified:
                logging.info("[%s] Provider '%s' has not been updated since last update. Continuing on to next provider in registry.", JOB_NAME, provider)
                continue

            # Just delete all triples in the context
            logging.info("[%s] Deleting triples in context %s.", JOB_NAME, provider)
            repository.delete_triples_about('?s', context=provider)

            data_dumps = void_model[provider_dataset]['dumps']

            for dump in data_dumps:
                logging.info("[%s] Processing provider '%s' dataset '%s' dump '%s'.", JOB_NAME, provider, provider_dataset, dump)

                # Create a temporary name for the file
                outfilename = datetime.datetime.now().strftime("%s-%f")

                try:
                    urllib.urlretrieve(dump, outfilename)
                except:
                    logging.error("[%s] Failed to fetch the void file at '%s'. Skipping dump file.", JOB_NAME, dump)
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

                # Import the file
                logging.info("[%s] Importing temp file '%s' into named graph '%s'.", JOB_NAME, outfilename, provider)
                repository.import_from_file(outfilename, context=provider, fmt=dump_file_format)

                # Delete the temp file
                try:
                    os.remove(outfilename)
                except:
                    logging.exception("[%s] Failed to delete temporary file located at '%s'.", JOB_NAME, outfilename)

                # Update registry file on disk
                registry_file[provider]['modified'] = modified
                registry.save_registry(registry_filepath, registry_file)


def export():
    """Export the repository as Turtle."""
    JOB_NAME = "EXPORT"
    logging.info("[%s] Job started.", JOB_NAME)

    s = Store(SESAME_HOST, SESAME_PORT)
    r = Repository(s, SESAME_REPOSITORY)

    # Establish the location of the export file
    # The else case will run when not running in a container
    if os.path.isdir('/www/'):
        export_filepath = '/www/exprort.ttl'
    else:
        export_filepath = 'exprort.ttl'

    with open(export_filepath, 'wb') as f:
        exported_text = r.export()
        f.write(exported_text.encode('utf-8'))


def status():
    """Gets the status of the system and prints to stdout."""
    JOB_NAME = "STATUS"
    logging.info("[%s] Job started.", JOB_NAME)

    s = Store(SESAME_HOST, SESAME_PORT)
    r = Repository(s, SESAME_REPOSITORY)

    logging.info("[%s] Repository size is '%d'.", JOB_NAME, r.size())
