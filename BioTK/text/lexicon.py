import collections

from BioTK.io.cache import download

def common_words(n=1000):
    """
    Return the most common words from a few popular Project Gutenberg novels
    (presumably a decent proxy for English) in lowercase.

    Parameters
    ----------
    n : int, optional
        The number of most common words to return.
    """
    corpus_urls = [
            "http://gutenberg.org/ebooks/%s.txt.utf-8" % id
            for id in [
                1342,   # Pride and Prejudice 
                135,    # Les Miserables
                11,     # Alice's Adventures in Wonderland
                1661    # The Adventures of Sherlock Holmes
            ]
    ]

    counts = collections.Counter()
    for url in corpus_urls:
        with open(download(url)) as h:
            for line in h:
                for token in line.lower().split():
                    counts[token] += 1
    return set([c[0] for c in counts.most_common(n)])
