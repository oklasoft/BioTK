import os

from .math import *

import logging
logging.basicConfig(level=logging.INFO)

try:
    from .version import version as __version__
except ImportError:
    __version__ = "HEAD"

def data(relpath):
    """
    Get an absolute path to a data resource that comes packaged with BioTK.
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 
        "data", relpath))
