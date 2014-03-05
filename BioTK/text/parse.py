"""
Biomedical natural language parsing.
"""
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

class PCFGParser(object):
    def __init__(self):
        pass

treebank_path = "/home/gilesc/Data/GENIA/genia-treebank/division/dev.trees"
trees = Treebank.parse(treebank_path)
tagger = HMMTagger.train(trees)
print(tagger.predict([t.word for t in trees[0].tokens]))
print([t.tag for t in trees[0].tokens])
