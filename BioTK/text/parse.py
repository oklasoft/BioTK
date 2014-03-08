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

        def handle_node(node):
            pass
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
