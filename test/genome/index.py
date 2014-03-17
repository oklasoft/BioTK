import gzip

from BioTK.io import BEDFile, download
from BioTK.genome.index import RAMIndex

def test():
    url = "http://github.com/arq5x/chrom_sweep/blob/master/knownGene.bed.gz?raw=true"
    path = download(url)
    index = RAMIndex()

    with gzip.open(path, "rt") as handle:
        for region in BEDFile(handle):
            index.add(region)
    index.build()

    result = index.search("chr1", 0, 1000000)
    assert(len(result) == 83)
