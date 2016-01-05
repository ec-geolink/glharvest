"""debug.py

General debug script.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
# sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'd1lod'))
sys.path.append("/Users/mecum/src/glharvest/d1lod/")
import logging
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] %(message)s')

import requests
from glharvest import util, void, registry, jobs

def main():
    jobs.update()
    # jobs.export()
    # jobs.status()


if __name__ == "__main__":
    main()
