"""parse_void.py

Parse the VoID file at the given URI
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))


import requests
from glharvest import util, void

def main():
    args = sys.argv

    if len(args) < 2:
        print "Wrong number of arguments. Try `python parse_void.py http://someurl.com`"
        return

    # Decide format to use (default or provided)
    void_format = "rdfxml"

    if len(args) == 3 and len(args[2]) > 0:
        void_format = args[2]

    filepath = args[1]
    print "Getting VoID file at %s." % filepath

    # If web...
    if filepath.startswith("http"):
        r = requests.get(args[1])

        if r.status_code != 200:
            print "Status code was not 200. Was %d instead. Exiting." % r.status_code
            return

        void_text = r.text
    else:
        if not os.path.isfile(filepath):
            print "Couldn't find file locally and didn't think file was a web URL (%s). Exiting." % filepath

        void_text = None

        with open(filepath, 'rb') as f:
            void_text = f.read()

        if void_text is None:
            print "Failed to read in void file from %s. Exiting." % filepath

    model = util.load_string_into_model(void_text, void_format)
    parsed = void.parse_void_model(model)
    print parsed



if __name__ == "__main__":
    main()
