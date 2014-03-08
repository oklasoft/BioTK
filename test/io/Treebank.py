import io

from BioTK.io import Treebank

TREEBANK = """
(S1 (S (NP (NP (NN Generation)) (PP (IN of) (NP (NP (JJ CD1+RelB+) (JJ dendritic) (NNS cells)) (CC and) (NP (ADJP (JJ tartrate-resistant) (NN acid) (JJ phosphatase-positive)) (JJ osteoclast-like) (JJ multinucleated) (JJ giant) (NNS cells)))) (PP (IN from) (NP (JJ human) (NNS monocytes))) (. .))))
(S1 (S (S (NP (PRP We)) (ADVP (RB previously)) (VP (VBD showed) (SBAR (IN that) (S (NP (NP (NP (JJ granulocyte-macrophage) (JJ colony-stimulating) (NN factor)) (PRN (-LRB- -LRB-) (NP (NN GM-CSF)) (-RRB- -RRB-))) (CC and) (NP (NP (NN macrophage) (JJ colony-stimulating) (NN factor)) (PRN (-LRB- -LRB-) (NP (NN M-CSF)) (-RRB- -RRB-)))) (VP (VBP stimulate) (NP (NP (DT the) (NN differentiation)) (PP (IN of) (NP (JJ human) (NNS monocytes))) (PP (IN into) (NP (NP (CD two) (ADJP (RB phenotypically) (JJ distinct)) (NNS types)) (PP (IN of) (NP (NNS macrophages)))))))))) (. .))))
"""

def test_parse():
    with io.StringIO(TREEBANK) as h:
        trees = Treebank.parse(h)
    assert(len(trees) == 2)

def test_fetch():
    trees = Treebank.fetch("GENIA")
    assert(len(trees) == 1361)
