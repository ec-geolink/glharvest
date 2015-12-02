"""jobs.py

Jobs for the Harvest System.
"""

import requests
import datetime

import sys
sys.path.append('/Users/mecum/src/d1lod/d1lod')
from d1lod.sesame import Store, Repository

from glharvest import registry, void, util


def dowork():
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
    regfile = registry.parse_registry_file('registry.yml')

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

                s = Store('localhost')

                # if s.hasRepository(provider):
                    # s.deleteRepository(provider)

                sr = Repository(s, 'test')
                sr.import_from_text(r.text, context=provider)

                # Update registry file on disk
                # regfile[provider]['modified'] = datetime.date.today()
                # registry.save_registry("registry.yml", regfile)



            else:
                print "datadump has not been updated since the last visit. Doing nothing."


if __name__ == "__main__":
    dowork()
