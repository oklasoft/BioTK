"""
Download, parse, and manipulate Gene Ontology term definitions and term-gene
mappings as either pandas.DataFrame or networkx.DiGraph objects.
"""

import gzip

import numpy as np
import networkx as nx
import pandas as pd

import BioTK.io
import BioTK.io.cache
import BioTK.io.OBO

GO = "http://www.geneontology.org/ontology/obo_format_1_2/gene_ontology_ext.obo"
GENE2GO = "ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2go.gz"

@BioTK.io.cache.RAMCache()
def _get_annotation(taxon_id):
    path = BioTK.io.cache.download(GENE2GO)
    with gzip.open(path, "r") as h:
        df = pd.read_table(h, skiprows=1, 
                header=None, names=("Taxon ID", "Gene ID", "Term ID", 
                    "Evidence", "Qualifier", "TermName", "PubMed", "Category"))
    return df.ix[df["Taxon ID"] == taxon_id,:].ix[:,
        ["Term ID","Gene ID","Evidence"]].drop_duplicates()

@BioTK.io.cache.RAMCache()
def _get_ancestry_table(g):
    rows = []
    for n in g.nodes():
        for ancestors in nx.dfs_successors(g, n).values():
            for ancestor in ancestors:
                rows.append((ancestor, n))
    return pd.DataFrame(rows, columns=["Ancestor", "Descendant"])

class GeneOntology(BioTK.io.OBO.Ontology):
    def __init__(self):
        path = BioTK.io.cache.download(GO)
        with open(path, "rt") as handle:
            o = BioTK.io.OBO.parse(handle)
        super(GeneOntology, self).__init__(o.terms, o.synonyms, o.relations)

    def annotation(self, taxon_id, recursive=False):
        A = _get_annotation(taxon_id)
        if recursive:
            inferred = A.merge(self.ancestry_table, 
                left_on="Term ID", right_on="Descendant")\
                        .ix[:,["Ancestor", "Gene ID", "Evidence"]]
            inferred.columns = ["Term ID", "Gene ID", "Evidence"]
            A = pd.concat([A, inferred], axis=0).drop_duplicates()
        return A

    def annotation_matrix(self, taxon_id, recursive=False):
        A = self.annotation(taxon_id, recursive=recursive)\
                .drop(["Evidence"], axis=1)\
                .drop_duplicates()
        A["Value"] = 1
        return A.pivot("Gene ID", "Term ID", "Value")\
                .fillna(0).astype(np.uint8)

    @property
    def ancestry_table(self):
        return _get_ancestry_table(self.to_graph())

    @property
    def concepts(self):
        ts = self.terms
        ix = ts["Name"].str.match("^(?:positive|negative) regulation of",
                as_indexer=True)
        coef = pd.Series(0, index=ts.index)
        coef[ts["Name"].str.match("^positive regulation of")] = 1
        coef[ts["Name"].str.match("^negative regulation of")] = -1
        ts["Concept"] = ts["Name"].str.replace(\
            "^(?:(?:positive|negative) )?regulation of ", "")
        ts["Directionality"] = coef
        return ts.reset_index().drop_duplicates().pivot(
                "Term ID", "Concept", "Directionality").astype(np.float32)

    def to_graph(self, taxon_id=None):
        g = super(GeneOntology, self).to_graph()
        if taxon_id:
            for term in g.nodes():
                g.node[term]["genes"] = set()

            A = self.annotation(taxon_id)
            for _, term, gene, evidence in A.to_records():
                g.node[term]["genes"].add(gene)
        return g
