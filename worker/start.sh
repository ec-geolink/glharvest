#!/bin/bash

# Wait for Sesame
# echo "Waiting for Sesame"
# until $(curl --output /dev/null --silent --head --fail http://graphdb:8080/openrdf-workbench/repositories/NONE/repositories); do
#     echo '.'
#     sleep 2
# done

# Start the Worker
sleep 10
echo "Starting Worker"

python -u work.py
