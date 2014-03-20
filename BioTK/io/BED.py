from BioTK.genome import Region

from .common import generic_open

class BEDFile(object):
    def __init__(self, handle_or_path):
        self._handle = generic_open(handle_or_path)

    def __enter__(self):
        return self

    def __iter__(self):
        keys = ["contig", "start", "end", "name", "score", "strand"]

        for line in self._handle:
            fields = line.strip().split("\t")
            attrs = dict(zip(keys, fields))
            attrs["start"] = int(attrs["start"])
            attrs["end"] = int(attrs["end"])
            if "score" in attrs:
              if "." == attrs["score"]:
                attrs["score"] = 0
              attrs["score"] = float(attrs["score"])
            yield Region(**attrs)

    def __exit__(self, *args):
        self._handle.close()

def parse(handle):
    return BEDFile(handle)
