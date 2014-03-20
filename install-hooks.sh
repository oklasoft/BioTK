#!/usr/bin/env bash

for file in hooks/*; do
    echo "Installing git hook:" $file 1>&2
    ln -rs $file .git/hooks 2> /dev/null || true
done
