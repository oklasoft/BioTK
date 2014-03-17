#!/usr/bin/env bash

for file in hooks/*; do
    ln -rs $file .git/hooks
done
