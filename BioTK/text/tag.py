"""
Part-of-speech (POS) tagging algorithms.
"""

import numpy as np

from sklearn import hmm

def _index_positions(items):
    return dict(list(map(reversed, enumerate(items))))

class ITagger(object):
    @staticmethod
    def train(tokens):
        raise NotImplementedError

class HMMTagger(ITagger):
    """
    A POS Tagger based on the classic Hidden Markov Model approach.
    """

    # TODO: The emission probability for tags on unknown words is
    #   uniform, should be the same probability as the average for
    #   known words

    def __init__(self, words, tags, model):
        self._words = words
        self._tags = tags
        self._word_index = _index_positions(words)
        self._tag_index = _index_positions(tags)
        self._model = model

    @staticmethod
    def train(trees):
        corpus = [list(t.tokens) for t in trees]
        words = list(sorted(set([t.word for c in corpus for t in c])))
        tags = list(sorted(set([t.tag for c in corpus for t in c])))
        word_index = _index_positions(words)
        tag_index = _index_positions(tags)

        transition = np.zeros((len(tags), len(tags)))
        start = np.zeros((len(tags),))
        emission = np.zeros((len(tags), len(words)+1))
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
        x = [self._word_index.get(w, len(self._words)) for w in words]
        logprob, tag_codes = self._model.decode(x)
        return [self._tags[code] for code in tag_codes]
