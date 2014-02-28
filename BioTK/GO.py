"""
Download, parse, and manipulate Gene Ontology term definitions and term-gene
mappings as either pandas.DataFrame or networkx.DiGraph objects.
"""

import gzip

import networkx as nx
import pandas as pd

import BioTK.cache
import BioTK.OBO

GO = "http://www.geneontology.org/ontology/obo_format_1_2/gene_ontology_ext.obo"
GENE2GO = "ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2go.gz"

@BioTK.cache.RAMCache()
def _get_annotation(taxon_id):
    path = BioTK.cache.download(GENE2GO)
    with gzip.open(path, "r") as h:
        df = pd.read_table(h, skiprows=1, 
                header=None, names=("TaxonID", "GeneID", "TermID", 
                    "Evidence", "Qualifier", "TermName", "PubMed", "Category"))
    return df.ix[df["TaxonID"] == taxon_id,:].ix[:,
        ["TermID","GeneID","Evidence"]]

class GeneOntology(BioTK.OBO.Ontology):
    def __init__(self):
        path = BioTK.cache.download(GO)
        with open(path, "rt") as handle:
            o = BioTK.OBO.parse(handle)
        super(GeneOntology, self).__init__(o.terms, o.synonyms, o.relations)

    def annotation(self, taxon_id):
        return _get_annotation(taxon_id)

    def to_graph(self, taxon_id):
        g = super(GeneOntology, self).to_graph()
        for term in g.nodes():
            g.node[term]["genes"] = set()

        A = self.annotation(taxon_id)
        for _, term, gene, evidence in A.to_records():
            g.node[term]["genes"].add(gene)
        return g
