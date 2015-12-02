"""jobs.py

Jobs for the Harvest System.
"""

import os
import requests
import datetime

import sys
sys.path.append('/d1lod')
from d1lod.sesame import Store, Repository

from glharvest import registry, void, util

SESAME_HOST = os.getenv('GRAPHDB_PORT_8080_TCP_ADDR', 'localhost')
SESAME_PORT = os.getenv('GRAPHDB_PORT_8080_TCP_PORT', '8080')
SESAME_REPOSITORY = 'test'

def main_job():
    """The main worker method for the Harvest System.

    1. Parse the registry file.
    2. For each provider in the registry,
        2a. Try to find their VoID file
        2b. Parse that VoID file
        2c. Determine if work needs to be done
            2c1. If none, go to the next provider
            2c2. If the modified time is different
                2c2a. Grab the data dump
                2c2b. Import the triples
                2c2c. Update the registry
    """

    # Parse registry file
    print "Parsing registry file."
    regfile = registry.parse_registry_file('/glharvest/registry.yml')

    if regfile is None:
        print "Failed to parse registry file. Exiting."
        return

    print "  %d provider(s) found." % len(regfile)

    for provider in regfile:
        print "Processing provider: `%s`." % provider

        # Void dump location
        if 'void' not in regfile[provider]:
            print "Location of VoID dataset not found for this provider in the registry. Skipping."
            continue

        voidfile = regfile[provider]['void']

        # Modified value
        if 'modified' not in regfile[provider]:
            print "Location of VoID dataset not found for this provider in the registry."
            provider_modified = None
        else:
            provider_modified = regfile[provider]['modified']

        # Get and parse the VoID file
        r = None

        try:
            r = requests.get(voidfile)
        except:
            print "Failed to get voidfile located at `%s`." % voidfile

        if r is None:
              continue

        model = util.load_string_into_model(r.text, format="turtle")
        void_model = void.parse_void_model(model)

        print void_model

        # Process the graph
        for graph in void_model:
            if 'modified' not in void_model[graph]:
                print "Graph found in VoID dump did not have dcterms:modified value. Skipping."

            modified = void_model[graph]['modified']

            # Parse datestring parts as ints
            try:
                year, month, day = [int(part) for part in modified.split("-")]
            except:
                print "Failed to parse datetime parts from string: `%s`. Skipping." % modified
                continue

            modified_dt = datetime.date(year, month, day)
            print "Registry says modified should be %s and the VoID dump says %s." % (provider_modified, modified_dt)

            if modified_dt > provider_modified:
                print "datadump has been updated since the last visit. We should fetch and import it."

                try:
                    void_location = void_model[graph]['dataDump']
                    r = requests.get(void_location)
                except:
                    print "Failed to fetch the void file at `%s`. Skipping." % void_location
                    # continue

                s = Store(SESAME_HOST, SESAME_PORT)

                # if s.hasRepository(provider):
                    # s.deleteRepository(provider)

                sr = Repository(s, SESAME_REPOSITORY)
                sr.import_from_text(r.text, context=provider)

                # Update registry file on disk
                regfile[provider]['modified'] = datetime.date.today()
                registry.save_registry("registry.yml", regfile)
            else:
                print "datadump has not been updated since the last visit. Doing nothing."


def status_job():
    """Gets the status of the system and prints to stdout."""
    print "Getting the status of the system."

    s = Store(SESAME_HOST, SESAME_PORT)
    r = Repository(s, SESAME_REPOSITORY)

    print "Repository size is %d" % r.size()


if __name__ == "__main__":
    dowork()
