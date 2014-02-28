from BioTK.genome.region import Region

def test_create_region():
    r = Region("chr1", 1, 5, strand=".")
