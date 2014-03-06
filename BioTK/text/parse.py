"""
Biomedical natural language parsing.
"""

# Parsing:
# - http://www.cs.utexas.edu/~mooney/cs388/slides/stats-parsing.ppt
# - http://www.cs.grinnell.edu/~pricerhy/csc205/cyk.py
# - Jurafsky & Martin pp. 438ff

# TODO:
# - handle unseen words in HMMTagger (add extra column in matrix)
# - add lexicalize() function to Tree()

import numpy as np

from sklearn import hmm

from BioTK.io import Treebank

class ITagger(object):
    def train(tokens):
        pass

def _index_positions(items):
    return dict(list(map(reversed, enumerate(items))))

class HMMTagger(ITagger):
    def __init__(self, words, tags, model):
        self._words = words
        self._tags = tags
        self._word_index = _index_positions(words)
        self._tag_index = _index_positions(tags)
        self._model = model

    @staticmethod
    def train(trees):
        corpus = [t.tokens for t in trees]
        words = list(sorted(set(t.word for c in corpus for t in c)))
        tags = list(sorted(set(t.tag for c in corpus for t in c)))
        word_index = _index_positions(words)
        tag_index = _index_positions(tags)

        transition = np.zeros((len(tags), len(tags)))
        start = np.zeros((len(tags),))
        emission = np.zeros((len(tags), len(words)))
        for s in corpus:
            for i,t in enumerate(s):
                tag_ix = tag_index[t.tag]
                word_ix = word_index[t.word]
                emission[tag_ix, word_ix] += 1
                if i == 0:
                    start[tag_ix] += 1
                else:
                    transition[tag_index[s[i-1].tag], tag_ix] += 1

        start /= start.sum()
        normalize_rows = lambda x: (x.T / x.sum(axis=1)).T
        transition = normalize_rows(transition+1)
        emission = normalize_rows(emission+1)

        model = hmm.MultinomialHMM(n_components=len(tags), 
                transmat=transition,
                startprob=start)
        model.emissionprob_ = emission
        return HMMTagger(words, tags, model)
    
    def predict(self, words):
        x = [self._word_index[w] for w in words]
        logprob, tag_codes = self._model.decode(x)
        return [self._tags[code] for code in tag_codes]
        
class IParser(object):
    @staticmethod
    def train(trees):
        raise NotImplementedError

    def parse(tokens):
        raise NotImplementedError

class RandomParser(object):
    def __init__(self):
        self._tags = set()

    @staticmethod
    def train(trees):
        p = RandomParser()

    def parse(tokens):
        pass

class CYKParser(object):
    @staticmethod
    def train(trees):
        pass

from .types import Token

class PCFG(object):
    def __init__(self, productions):
        self._productions = productions

    @staticmethod
    def build(trees):
        from collections import Counter
        i = 0
        dummy = {}
        c = Counter()

        #def handle_node(node):
        for tree in trees:
            for node in tree.nodes:
                if not isinstance(node, Token):
                    handle_node(node)

        return PCFG(dict(c.items()))

    def to_cnf(self):
        """
        Convert this generic PCFG to Chomsky Normal Form (CNF).
        """
        c = Counter()
        for p,n in self._productions.items():
            tag, p = p[0], p[1:]
            while len(p) > 2:
                tuple(p[:2])
                tag
            if len(p) <= 3:
                c[p] = n
            else:
                pass

def productions(node):
    lhs = node.tag
    rhs = [n.tag for n in node.children]
    is_terminal = [c.is_terminal for c in node.children]

class ChomskyNormalFormPCFG(PCFG):
    @staticmethod
    def build(trees):
        pass

treebank_path = "/home/gilesc/Data/GENIA/genia-treebank/division/dev.trees"
trees = Treebank.parse(treebank_path)
grammar = PCFG.build(trees[:5])

#tagger = HMMTagger.train(trees)
#print(tagger.predict([t.word for t in trees[0].tokens]))
#print([t.tag for t in trees[0].tokens])
