import base64
import gzip
import os
import shutil
import urllib.parse
import urllib.request

import BioTK.io.Aspera as Aspera

def copy_handle(src, dest):
    n = 0
    while True:
        s = src.read(1024)
        if not s:
            break
        n += len(s)
        dest.write(s)
    return n
        
def download(relative_url, cache_directory="/tmp/BioTK/NCBI", 
        compress=None, decompress=None,
        cache_size=100, return_path=False):
    """
    Download files from NCBI, with optional caching. The first argument is a
    relative URI to a NCBI file, omitting the host part of the URL.

    Example URI:
        '/geo/platforms/GPLnnn/GPL96/annot/GPL96.annot.gz'

    This cache first attempts to download the file using Aspera
    if it is available, then falls back to FTP download. Currently
    cannot download directories or handle recursion.
    """
    if compress is not None:
        raise NotImplementedError("The 'compress' option is not implemented.")

    os.makedirs(cache_directory, exist_ok=True)
    try:
        client = Aspera.Client()
        download = client.download
    except Aspera.Error:
        NCBI_FTP_BASE = "ftp://ftp.ncbi.nlm.nih.gov/"
        def download(url):
            url = urllib.parse.urljoin(NCBI_FTP_BASE, url)
            return urllib.request.urlopen(url)

    # FIXME: use system default encoding instead of utf-8
    path = os.path.join(cache_directory.encode("utf-8"), 
            base64.b64encode(relative_url.encode("utf-8")))
    if not os.path.exists(path):
        with download(relative_url) as stream:
            with open(path, "wb") as out:
                shutil.copyfileobj(stream, out)
                #n = copy_handle(stream, out)

    if return_path:
        return path
    else:
        if not decompress:
            return open(path, "rt")
        elif decompress == "gzip":
            return gzip.open(path, "rt")
        else:
            raise IOError("Invalid 'decompress' option.")
