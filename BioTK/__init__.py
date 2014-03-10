import logging
import os

logging.basicConfig(level=logging.INFO)

def data(relpath):
    """
    Get an absolute path to a data resource that comes packaged with BioTK.
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), relpath))
