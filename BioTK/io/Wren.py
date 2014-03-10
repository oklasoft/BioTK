"""
I/O for datasets specific to the Wren Lab.

Many of these use MS Access (I know...) and thus require MDBTools to be
installed so that the optional BioTK.io.MDB module can be compiled.
"""

from collections import defaultdict, namedtuple

from BioTK.io import MDB 

Term = namedtuple("Term", "id,name,synonyms")
Synonym = namedtuple("Synonym", "text,case_sensitive")

class SORD(object):
    def __init__(self, path):
       self._db = MDB.Database(path)

    @property
    def terms(self):
        terms = {}
        i = 0
        for row in self._db["tblObjectSynonyms"].records():
            id = row.RecordID
            name = row.Objectname
            synonym = row.Objectsynonym
            case_sensitive = row.CAPS_flag
            if not id in terms:
                terms[id] = Term(id, name, [])
            terms[id].synonyms.append(Synonym(synonym, case_sensitive))

            #i += 1
            #if i == 1000:
            #    break

        return terms
