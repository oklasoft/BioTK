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

    Term = namedtuple("Term", "id,name,synonyms")

    @property
    def terms(self):
        names = {}
        synonyms = defaultdict(list)
        for row in self._db["tblObjectSynonyms"].records():
            id = row.RecordID
            name = row.Objectname
            synonym = row.Objectsynonym
            names[id] = name
            synonyms[id].append(synonym)

        assert(set(names.keys()) == set(synonyms.keys()))

        for id in names.keys():
            yield SORD.Term(id, names[id], synonyms[id])

if __name__ == "__main__":
    path = "/home/gilesc/Data/SORD_Master_v31.mdb"
    db = SORD(path)
    for t in db.terms:
        print(t)
