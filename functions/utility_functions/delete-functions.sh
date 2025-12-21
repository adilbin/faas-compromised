#!/bin/bash

# Script to delete OpenFaaS functions (both yaml file and directory)

if [ $# -eq 0 ]; then
    echo "Usage: $0 <function-name> [function-name2] [function-name3] ..."
    echo "Example: $0 hash-generator data-validator"
    exit 1
fi

for name in "$@"; do
    yaml_file="${name}.yaml"
    dir_name="${name}"
    deleted=false
    
    if [ -f "$yaml_file" ]; then
        rm "$yaml_file"
        echo "Deleted: $yaml_file"
        deleted=true
    fi
    
    if [ -d "$dir_name" ]; then
        rm -rf "$dir_name"
        echo "Deleted: $dir_name/"
        deleted=true
    fi
    
    if [ "$deleted" = false ]; then
        echo "Nothing to delete for '$name': no file or directory found"
    fi
done

echo "Done!"

