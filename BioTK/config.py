"""
Configuration of global options.
"""

import os

# TODO: allow a lot of this to be set with a config file

CONFIG_DIR = os.path.join(os.getenv("HOME"),
        ".config", "BioTK")
CACHE_DIR = os.path.join(os.getenv("HOME"),
        ".cache", "BioTK")

for dir in [CONFIG_DIR, CACHE_DIR]:
    if not os.path.isdir(dir):
      os.makedirs(dir, exist_ok=True)
