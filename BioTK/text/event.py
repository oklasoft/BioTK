"""
Event and relation extraction.
"""

import gzip
import json
import sys
import fileinput

import networkx as nx

import BioTK

class DependencyGraph(nx.DiGraph):
    def __init__(self, words, tags, edges):
        super(DependencyGraph, self).__init__()
        for i,(w,t) in enumerate(zip(words, tags)):
            self.add_node(i, word=w, tag=t)
        for gov,dep,type in edges:
            self.add_edge(dep, gov, type=type)

    def __repr__(self):
        return "<DependencyGraph with %s nodes and %s edges>" % (len(self), len(self.edges()))

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
    def __init__(self):
        # A map from each IIT to its stem
        self.IIT = {}
        with open(BioTK.data("text/RelEx-IITs")) as handle:
            for line in handle:
                stem, words = line.split(":")
                for word in words.split("|"):
                    self.IIT[word] = stem

    def extract(self, dgraph):
        pass

from BioTK.io.cache import memcached
from BioTK.io import Wren 
from BioTK.text import AhoCorasick

def get_terms():
    path = "/home/gilesc/Data/SORD_Master_v31.mdb"
    db = Wren.SORD(path)
    return db.terms

if __name__ == "__main__":
    trie = AhoCorasick.Trie()

    terms = get_terms()
    for t in terms.values():
        for s in t.synonyms:
            trie.add(s.text, key=t.id)
    trie.build()
    print("Trie built...")

    with fileinput.input() as handle:
        n = 0
        for i,line in enumerate(handle):
            if i % 1000 == 0:
                print(i, n)
            for m in trie.search(line):
                n += 1

    #    for g in DependencyGraph.load(handle):
    #        print(repr(g))
