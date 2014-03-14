import mimetypes
import gzip
import bz2

def generic_open(path, mode="rt"):
    """
    Open a file path, bzip2- or gzip-compressed file path, 
    or URL in the specified mode.

    Not all path types support all modes. For example, a URL is not
    considered to be writable. 
    
    :param path: Path
    :type path: str
    :throws IOError: If the file cannot be opened in the given mode
    :throws FileNotFoundError: If the file cannot be found
    :rtype: :py:class:`io.IOBase` or :py:class:`io.TextIOBase`, 
      depending on the mode
    """

    # FIXME: detect zipped file based on magic number, not extension
    # FIXME: enable opening zipped file in text mode
    # FIXME: detect URLs and detect and unzip a zipped URL 
    # FIXME: allow caching of downloads

    if hasattr(path, "read"):
        return path

    type, compression = mimetypes.guess_type(path)

    if compression == "gzip":
        h = gzip.open(path, mode=mode)
    elif compression == "bzip2":
        h = bz2.BZ2File(h, mode=mode)
    else:
        h = open(path, mode=mode)
    return h
