import base64
import contextlib
import os
import tarfile
import zipfile

import pandas as pd

class Project(object):
    """
    Read data from an Agilent GeneSpring project TAR file.
    """
    def __init__(self, path):
        self._handle = tarfile.open(path)

    @property
    def expression(self):
        samples = {}

        for item in self._handle:
            if (item.path != "ENCODEFLAG") and (not item.isdir()):
                real_path = base64.standard_b64decode(item.path)\
                        .decode("utf-8")
                if not ".Sample_" in real_path:
                    continue
                with contextlib.closing(zipfile.ZipFile(
                    self._handle.extractfile(item))) as zf:
                    path = zf.namelist()[0]
                    with zf.open(path) as h:
                        df = pd.read_csv(h, index_col="ProbeID")
                        sample_id = df.columns[0].split("-")[1]
                        if sample_id in samples:
                            continue
                        df.columns = [c.split("-")[0] for c in df.columns]
                        samples[sample_id] = df["AVG_Signal"]

        df = pd.DataFrame.from_dict(samples)
        df.index.name = "Probe"
        df.columns.name = "Sample"
        return df

    def __del__(self):
        self.close()

    def close(self):
        self._handle.close()
