from BioTK.io.cache import memcached
from BioTK.text.types import Tree

from pyparsing import Word, Forward, Group, Suppress, OneOrMore

__all__ = ["parse", "sample"]

ch = "".join(set(map(chr, range(33, 127))) - set("()"))
LPAR, RPAR = map(Suppress, "()")
token = Word(ch)
tag = Word(ch)
node = Forward()
node <<= Group(LPAR + tag + OneOrMore(node | token) + RPAR)\
        .setParseAction(lambda s,l,t: tuple(t[0]))
treebank = OneOrMore(node)

@memcached()
def _parse(path):
    return list(treebank.parseFile(path))

def parse(path):
    return [Tree.from_list(tree) for tree in _parse(path)]

TREEBANK = """
(S1 (S (NP (NP (NN Generation)) (PP (IN of) (NP (NP (JJ CD1+RelB+) (JJ dendritic) (NNS cells)) (CC and) (NP (ADJP (JJ tartrate-resistant) (NN acid) (JJ phosphatase-positive)) (JJ osteoclast-like) (JJ multinucleated) (JJ giant) (NNS cells)))) (PP (IN from) (NP (JJ human) (NNS monocytes))) (. .))))
(S1 (S (S (NP (PRP We)) (ADVP (RB previously)) (VP (VBD showed) (SBAR (IN that) (S (NP (NP (NP (JJ granulocyte-macrophage) (JJ colony-stimulating) (NN factor)) (PRN (-LRB- -LRB-) (NP (NN GM-CSF)) (-RRB- -RRB-))) (CC and) (NP (NP (NN macrophage) (JJ colony-stimulating) (NN factor)) (PRN (-LRB- -LRB-) (NP (NN M-CSF)) (-RRB- -RRB-)))) (VP (VBP stimulate) (NP (NP (DT the) (NN differentiation)) (PP (IN of) (NP (JJ human) (NNS monocytes))) (PP (IN into) (NP (NP (CD two) (ADJP (RB phenotypically) (JJ distinct)) (NNS types)) (PP (IN of) (NP (NNS macrophages)))))))))) (. .))))
"""

def sample():
    return [Tree.from_list(t) for t in treebank.parseString(TREEBANK)]
