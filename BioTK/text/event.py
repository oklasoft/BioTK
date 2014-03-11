"""
Event and relation extraction.
"""

import gzip
import json
import sys
import fileinput
import itertools

import networkx as nx
import numpy as np

import BioTK

from BioTK.text.types import Token
from BioTK.text import AhoCorasick

class DependencyGraph(nx.DiGraph):
    def __init__(self, words=[], tags=[], edges=[], entities=None):
        super(DependencyGraph, self).__init__()
        self.entities = entities
        self.tokens = []
        for i,(w,t) in enumerate(zip(words, tags)):
            self.add_node(i, word=w, tag=t)
            self.tokens.append(Token(w, tag=t, index=i))
        for gov,dep,type in edges:
            self.add_edge(dep, gov, type=type)

    def __repr__(self):
        return "<DependencyGraph with %s nodes and %s edges>" \
                % (len(self), len(self.edges()))

    def to_dict(self):
        words, tags, edges = [], [], []
        for i in self.nodes():
            if i == -1:
                continue
            n = self.node[i]
            words.append(n["word"])
            tags.append(n["tag"])
        for dep, gov in self.edges():
            type = self[dep][gov]["type"]
            edges.append((gov,dep,type))
        out = {"words": words, "tags": tags, "edges": edges}
        if self.entities:
            out["entities"] = self.entities
        return out

def find_entities_in_tokens(trie, tokens):
    text = " ".join(tokens)
    end = np.cumsum(list(map(len, tokens))) + np.arange(len(tokens))
    start = np.array([0] + list(end[:-1]))
    matches = collections.defaultdict(set)

    for m in trie.search(text):
        ix = tuple(((start < m.end) & (end > m.start)).nonzero()[0])
        matches[m.key].add(ix)
    for k in matches:
        matches[k] = list(matches[k])
    return dict(matches.items())

class RelEx(object):
    """
    An implementation of Fundel et al 2007:
      RelEx - Relation extraction using dependency parse trees
    """
    def __init__(self):
        self.iit = {}
        with open(BioTK.data("text/RelEx-IITs")) as handle:
            for line in handle:
                stem, words = line.split(":")
                for word in words.split("|"):
                    self.iit[word] = stem

    def _extract_one(self, ug, ix1, ix2):
        assert(ix1 < ix2)

        try:
            path = nx.shortest_path(ug, ix1, ix2)
        except nx.NetworkXNoPath:
            return

        if not len(path) >= 3:
            return
        if not ug[ix1][path[1]]["type"] == "nsubj":
            return
        if not ug[path[-2]][ix2]["type"] == "dobj":
            return

        for ix in path[1:-2]:
            n = ug.node[ix]
            if n["tag"].startswith("V"):
                verb = n["word"]
                if verb in self.iit:
                    stem = self.iit[verb]
                    return stem

    def extract(self, g, entities):
        ug = g.to_undirected()
        relations = []

        for k1,ixs1 in entities.items():
            ixs1 = [ix for ixs in ixs1 for ix in ixs]
            for k2,ixs2 in entities.items():
                if k1 >= k2:
                    continue
                ixs2 = [ix for ixs in ixs2 for ix in ixs]
                for ix1, ix2 in itertools.product(ixs1, ixs2):
                    if ix1 == ix2:
                        # Shouldn't happen ...
                        continue
                    reverse = ix1 > ix2
                    if reverse:
                        ix1, ix2 = ix2, ix1
                    r = self._extract_one(ug, ix1, ix2)
                    if r is not None:
                        rel = (r,k2,k1) if reverse else (r,k1,k2)
                        relations.append(rel)
                        break
        return relations

from BioTK.io.cache import memcached
from BioTK.io import Wren 
from BioTK.text.lexicon import common_words

from collections import defaultdict

@memcached()
def get_synonyms():
    cw = common_words(50000)

    path = "/home/gilesc/Data/SORD_Master_v31.mdb"
    db = Wren.SORD(path)
    df = db.synonyms
    ix = (df["Synonym"].str.len() > 3) & \
        [s not in cw for s in df["Synonym"]]
    return df.ix[ix,:]

if __name__ == "__main1__":
    trie = AhoCorasick.MixedCaseSensitivityTrie(boundary_characters=" ;,.!?")

    import collections
    #print("Retrieving synonyms ...")
    synonyms = get_synonyms().ix[:,["Term ID", "Synonym", "Case Sensitive"]]
    #print("Adding synonyms to trie ...")
    for _, id, text, case_sensitive in synonyms.to_records():
        trie.add(text, bool(case_sensitive), key=id)

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

    #print("Building trie ...")
    trie.build()

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

    #relex = RelEx(trie)

    with fileinput.input() as handle:
        for line in handle:
            document = json.loads(line)
            for sentence in document:
                g = DependencyGraph(**sentence)
                entities = find_entities_in_tokens(trie, sentence["words"])
                if entities:
                    g.entities = entities
                    print(g.to_dict())

if __name__ == "__main__":
    rx = RelEx()

    with fileinput.input() as handle:
        for i,line in enumerate(handle):
            if i % 1000 == 0:
                print("**", i)
            sentence = eval(line)
            g = DependencyGraph(**sentence)
            if len(g.entities) < 2:
                continue
            for rel in rx.extract(g, g.entities):
                print(rel)
