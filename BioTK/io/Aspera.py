"""
Python wrapper for the Aspera client (used for fast downloads from NCBI
server).
"""

# FIXME: if the user hasn't manually used ascp before, download()
# will hang, asking the user to trust the remote host and add
# remote key to PuTTY cache

# TODO: download binary if necessary?
# TODO: allow option to AsperaClient.download() to background the download
#   into other process or thread
# TODO: if binary is not found, add instructions into error message
#   about how to get it
# TODO: allow multiple source files to be given to download() ?

import os
import sys
import subprocess as sp
import tempfile

def _find_binary():
    """
    Search PATH for ascp. Returns None if it could not be found.
    """
    search_folders = list(sys.path)
    search_folders.append(os.path.expanduser("~/.aspera/connect/bin/"))
    for folder in search_folders:
        path = os.path.join(folder, "ascp")
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path

class Error(IOError):
    pass

class Client(object):
    def __init__(self, 
            user="anonftp", 
            host="ftp-private.ncbi.nlm.nih.gov", 
            limit=200, # in MB
            key_file="~/.aspera/connect/etc/asperaweb_id_dsa.putty"):
        assert isinstance(limit, int)

        self._binary_path = _find_binary()
        if not self._binary_path:
            raise Error("Aspera client binary (ascp) could not be found.")

        self._user = user
        self._host = host
        self._limit = limit
        self._key_file = os.path.expanduser(key_file)

    def download(self, source, decompress=None):
        """
        Download a single file from this Aspera server,
        returning an open file handle to the resulting file.

        This handle will delete the underlying temporary file when it is
        closed, so use shutil.copyfile or similar to persist the data.
        """
        assert decompress == None, "Decompression not implemented."

        source_uri = "%s@%s:/%s" % (self._user, self._host, source.lstrip("/"))
        handle = tempfile.NamedTemporaryFile(delete=True)
        destination = handle.name
        args = [self._binary_path, 
                "-i", self._key_file, 
                "-l", "%sM" % self._limit,
                source_uri, destination]
        p = sp.Popen(args, stdin=sp.PIPE, stdout=sp.DEVNULL, stderr=sp.PIPE)
        p.wait()
        if p.returncode:
            msg = p.stderr.read().decode("utf-8").strip()
            raise Error(msg)
        return handle
