"""
I/O for datasets specific to the Wren Lab.

Many of these use MS Access (I know...) and thus require MDBTools to be
installed so that the optional BioTK.io.MDB module can be compiled.
"""

from collections import defaultdict, namedtuple

from BioTK.io import MDB 

class SORD(object):
    def __init__(self, path):
       self._db = MDB.Database(path)

    def _get_synonyms(self):
        df = self._db["tblObjectSynonyms"].to_data_frame()
        df = df.iloc[:,[0,1,3,2,4,8,11]]
        df.columns = ["Term ID", "Name", "Synonym", "Category",
                "Source ID", "Frequency", "Case Sensitive"]
        df.index.name = "Synonym ID"
        return df

    @property
    def synonyms(self):
        df = self._get_synonyms()
        return df.drop("Name", axis=1)

    #@property
    #def terms(self):
    #    pass
