"""
Read syntactic trees from a treebank file (in PTB format).
"""
import io
import tarfile

from pyparsing import Word, Forward, Group, Suppress, OneOrMore

from BioTK.io.cache import memcached, download
from BioTK.io import generic_open
from BioTK.text.types import Tree

__all__ = ["parse", "fetch"]

ch = "".join(set(map(chr, range(33, 127))) - set("()"))
LPAR, RPAR = map(Suppress, "()")
token = Word(ch)
tag = Word(ch)
node = Forward()
node <<= Group(LPAR + tag + OneOrMore(node | token) + RPAR)\
        .setParseAction(lambda s,l,t: tuple(t[0]))
treebank = OneOrMore(node)

@memcached()
def _parse(handle):
    return list(treebank.parseString(handle.read()))

def parse(handle_or_path):
    with generic_open(handle_or_path) as handle:
        return [Tree.from_list(tree) for tree in _parse(handle)]

def fetch(name):
    if not name == "GENIA":
        raise Exception("Unknown treebank.")
    url = "http://bllip.cs.brown.edu/download/genia1.0-division-rel1.tar.gz"
    with tarfile.open(download(url), "r:gz") as tgz:
        # Also: test.trees train.trees
        with tgz.extractfile("genia-dist/division/dev.trees") as h:
            with io.TextIOWrapper(h, encoding="utf8") as h:
                return parse(h)
