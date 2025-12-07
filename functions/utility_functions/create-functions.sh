#!/bin/bash

# Script to create new OpenFaaS functions using faas-cli
# Only creates functions if the yaml file or directory doesn't already exist

if [ $# -eq 0 ]; then
    echo "Usage: $0 <function-name> [function-name2] [function-name3] ..."
    echo "Example: $0 hash-generator data-validator"
    exit 1
fi

for name in "$@"; do
    yaml_file="${name}.yaml"
    dir_name="${name}"
    
    if [ -f "$yaml_file" ]; then
        echo "Skipping '$name': $yaml_file already exists"
    elif [ -d "$dir_name" ]; then
        echo "Skipping '$name': directory $dir_name/ already exists"
    else
        echo "Creating function: $name"
        faas-cli new "$name" --lang python3-http-debian --yaml "$yaml_file"
    fi
done

echo "Done!"

