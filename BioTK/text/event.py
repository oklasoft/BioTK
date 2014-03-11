"""
Event and relation extraction.
"""

import gzip
import json
import sys
import fileinput

import networkx as nx
import numpy as np

import BioTK

from BioTK.text.types import Token
from BioTK.text import AhoCorasick

class DependencyGraph(nx.DiGraph):
    def __init__(self, words, tags, edges):
        super(DependencyGraph, self).__init__()
        self.tokens = []
        for i,(w,t) in enumerate(zip(words, tags)):
            self.add_node(i, word=w, tag=t)
            self.tokens.append(Token(w, tag=t, index=i))
        for gov,dep,type in edges:
            self.add_edge(dep, gov, type=type)

    def __repr__(self):
        return "<DependencyGraph with %s nodes and %s edges>" \
                % (len(self), len(self.edges()))

    @staticmethod
    def load(handle):
        # FIXME: should this be a member of DG?
        for line in handle:
            document = json.loads(line)
            for sentence in document:
                yield DependencyGraph(sentence["words"], 
                        sentence["tags"], sentence["edges"])

class RelEx(object):
    """
    An implementation of Fundel et al 2007:
      RelEx - Relation extraction using dependency parse trees
    """
    def __init__(self, trie):
        self.iit_trie = AhoCorasick.Trie()
        with open(BioTK.data("text/RelEx-IITs")) as handle:
            for line in handle:
                stem, words = line.split(":")
                for word in words.split("|"):
                    self.iit_trie.add(word, key=stem)
        self.iit_trie.build()

        self.entity_trie = trie

    def extract(self, g):
        tokens = [t.word for t in g.tokens]
        text = " ".join(tokens)
        end = np.cumsum(list(map(len, tokens))) + np.arange(len(tokens))
        start = np.array([0] + list(end[:-1]))
        matches = collections.defaultdict(set)

        for m in trie.search(text):
            ix = tuple(((start < m.end) & (end > m.start)).nonzero()[0])
            matches[m.key].add(ix)

        for k1,ixs1 in matches.items():
            ixs1 = [ix for ixs in ixs1 for ix in ixs]
            for k2,ixs2 in matches.items():
                if k1 >= k2:
                    continue
                ixs2 = [ix for ixs in ixs2 for ix in ixs]
                print(ixs1, ixs2)
        return []

from BioTK.io.cache import memcached
from BioTK.io import Wren 
from BioTK.text.lexicon import common_words

def get_terms():
    path = "/home/gilesc/Data/SORD29.mdb"
    db = Wren.SORD(path)
    return db.terms

if __name__ == "__main__":
    trie = AhoCorasick.MixedCaseSensitivityTrie(boundary_characters=" ;,.!?")

    cw = common_words(50000)
    import collections

    terms = get_terms()
    for t in terms.values():
        for s in t.synonyms:
            if (len(s.text) < 3) or (s.text.lower() in cw):
                continue
            trie.add(s.text, case_sensitive=s.case_sensitive, key=t.id)

    """
    terms = collections.defaultdict(list)
    with open("/home/gilesc/Data/gene_info.Hs") as handle:
        for line in handle:
            fields = line.split("\t")
            gene_id = int(fields[1])
            if fields[4] == "-":
                continue
            for synonym in fields[4].split("|"):
                if len(synonym) < 3:
                    continue
                if not synonym.lower() in cw:
                    terms[gene_id].append(synonym)
                    trie.add(synonym, key=gene_id)
    """

    trie.build()
    print("Trie built...")

    """
    c = collections.Counter()
    with fileinput.input() as handle:
        n = 0
        for i,line in enumerate(handle):
            if i % 1000 == 0:
                print(i,n)
            if i >= 100000:
                break
            for m in trie.search(line):
                n += 1
                c[m.key] += 1
    
    for id, count in c.most_common(5):
        print(id, count, terms[id])
    """


    relex = RelEx()
    with fileinput.input() as handle:
        for g in DependencyGraph.load(handle):
            for rel in relex.extract(g):
                print(rel)
