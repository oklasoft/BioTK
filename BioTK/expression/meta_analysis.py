"""
How to organize the data/class hierarchy?
    taxon -> platform -> (experiment / platform subset?) -> sample

Currently the setup is a little confusing because there
is a Platform object which shouldn't be confused with
a BioTK.io.GEO.GPL object.
"""
# TODO: Check for existence before returning Taxon, Platform, etc.

import gzip
import pickle
from itertools import groupby

import h5py
import pandas as pd
import numpy as np

import BioTK.util
from BioTK.io import GEO, NCBI
from .preprocess import quantile_normalize

def _get_prefix(accession):
    return accession[:-3] + "nnn"

def unpickle_object(data):
    return pickle.loads(bytes(data))

def pickle_object(obj):
    return np.array(pickle.dumps(obj))

class Platform(object):
    """
    A container for all the expression samples performed on the
    same platform.
    """
    def __init__(self, group):
        self._group = group

    def expression(self, samples, collapse=None, normalize=False):
        F = self.features
        samples = list(samples)

        ix = self._sample_index()
        ix = sorted([ix[s] for s in samples])
        X = pd.DataFrame(self._group["expression"][ix,:],
                index=samples, columns=F.index).T
        X.index.name = "Feature"
        X.columns.name = "Sample"

        if collapse:
            # FIXME: handle probes mappings with '//'
            # FIXME: collapse by MAX mean
            X = X.groupby(F[collapse]).mean()
            X = X.ix[[(" /// " not in x) for x in X.index],:]
        if normalize:
            X = quantile_normalize(X)
        return X

    def attributes(self, summarize=True):
        P = self.samples
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

    def _sample_index(self):
        return dict(list(map(reversed, enumerate(self.samples.index))))

    @property
    def samples(self):
        return unpickle_object(self._group["sample"].value)

    @property
    def features(self):
        return unpickle_object(self._group["feature"].value)

    def _add_samples(self, geo_platform, it):
        """
        Add samples to this platform from a GEO Family iterator.
        """
        probes = geo_platform.table.index

        def expression(gsm):
            return np.array([gsm.expression.get(ix, np.nan)
                for ix in probes])

        n = len(probes)
        dataset = self._group.create_dataset("expression",
                dtype='f8', chunks=(1, n), maxshape=(None, n),
                compression="lzf",
                shape=(1, n))
        samples = []
        accessions = []

        chunk_size = 50
        end = 0
        for i,chunk in enumerate(BioTK.util.chunks(it, chunk_size)):
            start = end
            end = start + len(chunk)
            dataset.resize((end+1,n))
            data = np.zeros((len(chunk), n), dtype='f8')
            for j,gsm in enumerate(chunk):
                print("\t*", gsm.accession)
                accessions.append(gsm.accession)
                samples.append(pd.Series(gsm.attributes))
                data[j,:] = expression(gsm)[np.newaxis,:]
            dataset[start:end,:] = data

        samples = pd.DataFrame.from_records(samples,
                index=accessions)
        self._group.create_dataset("sample",
                data=pickle_object(samples))

class Taxon(object):
    """
    A container for all the different platforms belonging to a single
    taxon.
    """
    def __init__(self, group):
        self._group = group
        self.taxon_id = int(group.name.lstrip("/"))

    def __getitem__(self, accession):
        return self.platform(accession)

    def platform(self, accession):
        group = self._group[accession]
        return Platform(group)

    def _add_platform(self, geo_platform):
        group = self._group.create_group(geo_platform.accession)
        group.create_dataset("feature", 
                data=pickle_object(geo_platform.table))
        return self.platform(geo_platform.accession)

class ExpressionDB(object):
    def __init__(self, path):
        self._path = path
        self._store = h5py.File(path, "a")

    def __del__(self):
        self.close()

    def close(self):
        self._store.close()

    def add_taxon(self, taxon_id):
        key = "/%s" % taxon_id
        group = self._store.create_group(key)
        return self.taxon(taxon_id)

    def taxon(self, taxon_id):
        key = "/%s" % taxon_id
        self._store.require_group(key)
        group = self._store[key]
        return Taxon(group)

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

    def __contains__(self, taxon_id):
        return str(taxon_id) in self._store

    def add_family(self, accession_or_path):
        if accession_or_path.startswith("GPL"):
            accession = accession_or_path
            url = "/geo/platforms/GPL%snnn/%s/soft/%s_family.soft.gz" % \
                    (accession[3:-3], accession, accession)
            handle = NCBI.download(url, decompress="gzip")
        else:
            path = accession_or_path
            handle = gzip.open(path, "rt")

        with handle:
            it = GEO.Family._parse_single(handle)
            geo_platform = it.__next__()
            taxon_id = geo_platform.taxon_id
            if not geo_platform.taxon_id in self:
                taxon = self.add_taxon(taxon_id)
            else:
                taxon = self.taxon(taxon_id)
            platform = taxon._add_platform(geo_platform)
            platform._add_samples(geo_platform, it)
        return platform
      
def test():
    db = ExpressionDB("/home/gilesc/expression.h5")
    # errors on 341
    #for accession in [1355, 5424, 5426, 85]:
    for accession in [1355]:
        accession = "GPL%s" % accession
        path = "/home/gilesc/Data/GEO/rat/%s_family.soft.gz" % accession
        print("* Inserting %s" % accession)
        platform = db.add_family(path)

    #ss = platform.samples.index[:5]
    #X = platform.expression(ss)
    #print(X.head().T.head().T)

if __name__ == "__main__":
    test2()
