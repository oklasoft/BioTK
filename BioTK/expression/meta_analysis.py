"""
How to organize the data/class hierarchy?
    taxon -> platform -> (experiment / platform subset?) -> sample

Currently the setup is a little confusing because there
is a Platform object which shouldn't be confused with
a BioTK.io.GEO.GPL object.
"""
# TODO: Check for existence before returning Taxon, Platform, etc.

import warnings
from itertools import groupby

import pandas as pd

import BioTK.util
from BioTK.io import GEO, NCBI
from .preprocess import quantile_normalize

def _get_prefix(accession):
    return accession[:-3] + "nnn"

#class PlatformSubset(object):
#    pass

class Platform(object):
    """
    A container for all the expression samples performed on the
    same platform.
    """
    def __init__(self, taxon, accession):
        self.taxon = taxon
        self.accession = accession

    @property
    def path(self):
        return "%s/%s" % (self.taxon.path, self.accession)

    @property
    def _store(self):
        return self.taxon._store

    def expression(self, samples, collapse=None, normalize=False):
        groups = groupby(sorted(samples), _get_prefix)
        frames = []
        for prefix, accessions in groups:
            uri = "%s/expression/%s" % (self.path, prefix)
            frames.append(self.taxon._store.get(uri).ix[:,accessions])
        X = pd.concat(frames, axis=1)
        if collapse:
            # FIXME: handle probes mappings with '//'
            # FIXME: collapse by MAX mean
            F = self.features()
            X = X.groupby(F[collapse]).mean()
            X = X.ix[[(" /// " not in x) for x in X.index],:]
        if normalize:
            X = quantile_normalize(X)
        return X.ix[:,samples]

    def attributes(self, summarize=True):
        P = self._store.get("%s/sample" % self.path)
        if summarize:
            pattern = "[Aa]ge:\s*(\d+)(-\d+)? weeks"
            age = P["characteristics_ch1"].str.extract(pattern)\
                    .iloc[:,0].astype(float)
            pattern = "[Tt]issue:\s*([A-Za-z ]+)"
            tissue = P["characteristics_ch1"].str.extract(pattern)
            data = {"Age": age, "Tissue": tissue}
            return pd.DataFrame(data).dropna(axis=0, how="all")
        else:
            return P

    def features(self):
        return self._store.get("%s/feature" % self.path)

    def _add_samples(self, geo_platform, it):
        """
        Add samples to this platform from a GEO Family iterator.
        """
        prefixes = set()
        samples = None

        for prefix, gsms in groupby(it, lambda x: _get_prefix(x.accession)):
            if prefix in prefixes:
                raise Exception("This SOFT file is not sorted by GSM accession! Aborting. (Please report this as a bug).")
            prefixes.add(prefix)

            print("\t* Inserting", prefix)
            uri = "%s/expression/%s" % (self.path, prefix)
            gsms = list(gsms)

            accessions = [gsm.accession for gsm in gsms]
            expression = [gsm.expression for gsm in gsms]
            
            _samples = pd.DataFrame.from_records(
                    [gsm.attributes for gsm in gsms],
                    index=accessions)
            if samples is not None:
                samples = pd.concat([samples, _samples])
            else:
                samples = _samples
                
            expression = pd.DataFrame(expression, index=accessions)
            _, expression = \
                    geo_platform.table.T.align(expression, axis=1, join="left")

            self._store.put(uri, expression.T)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            uri = "%s/sample" % self.path
            self._store.put(uri, samples)

class Taxon(object):
    """
    A container for all the different platforms belonging to a single
    taxon.
    """
    def __init__(self, db, taxon_id):
        self._db = db
        self.taxon_id = taxon_id

    def __getitem__(self, accession):
        return self.platform(accession)

    @property
    def _store(self):
        return self._db._store

    @property
    def path(self):
        return "/%s" % self.taxon_id

    def _add_platform(self, geo_platform):
        uri = "/%s/%s/feature" % (self.taxon_id, geo_platform.accession)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self._store.put(uri, geo_platform.table)

        return self.platform(geo_platform.accession)

    def platform(self, accession):
        return Platform(self, accession)

class ExpressionDB(object):
    def __init__(self, path):
        self._path = path
        self._store = pd.HDFStore(path)

    def __del__(self):
        self.close()

    def close(self):
        self._store.close()

    def add_taxon(self, taxon_id):
        return Taxon(self, taxon_id)

    def taxon(self, taxon_id):
        return Taxon(self, taxon_id)

    def __getitem__(self, taxon_id):
        return self.taxon(taxon_id)

    def add_platform(self, accession):
        # We're storing by taxon ID which inexplicably is not
        #   in the GEO .annot files ...
        # To implement this method would need a Species Name <-> Taxon ID
        #   lookup.

        #platform = GEO.GPL.fetch(accession)
        #self._add_platform(platform)
        raise NotImplementedError

    #def platform(self, accession):
    #    return self._store.get(uri)

    def add_family(self, accession):
        url = "/geo/platforms/GPL%snnn/%s/soft/%s_family.soft.gz" % \
                (accession[3:-3], accession, accession)

        with NCBI.download(url, decompress="gzip") as handle:
            it = GEO.Family._parse_single(handle)
            geo_platform = it.__next__()
            taxon = self.taxon(geo_platform.taxon_id)
            platform = taxon._add_platform(geo_platform)
            platform._add_samples(geo_platform, it)
      
def test():
    db = ExpressionDB("/home/gilesc/expression.h5")
    # 341
    for accession in [1355, 5424, 5426, 85]:
        accession = "GPL%s" % accession
        print("* Inserting %s" % accession)
        db.add_family(accession)

    platform = db[10116]["GPL1355"]
    P = platform.attributes()
    age = P["Age"].dropna()
    X = platform.expression(age.index,
            collapse="ENTREZ_GENE_ID", normalize=True)
    return X.T.corrwith(age)


if __name__ == "__main__":
    test()
