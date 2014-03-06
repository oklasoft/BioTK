import numpy as np
cimport numpy as np

from cpython cimport bool

cdef class Node:
    cdef readonly:
        int index
        str tag

    cdef bool _is_terminal(self):
        raise NotImplementedError

    @property
    def is_terminal(self):
        return self._is_terminal()

cdef class Token(Node):
    cdef readonly str word

    def __init__(self, str word, str tag=None, int index=-1):
        self.index = index
        self.word = word
        self.tag = tag

    def __str__(self):
        return "%s/%s" % (self.word, self.tag)

    def __repr__(self):
        return "<Token %s>" % str(self)

    cdef bool _is_terminal(self):
        return True

cdef class InternalNode(Node):
    cdef readonly object children

    def __init__(self, int index, str tag, 
            np.ndarray[dtype=object, ndim=1] children):
        self.index = index
        self.tag = tag
        self.children = children

    @property
    def nodes(self):
        yield self
        cdef Node child
        for child in self.children:
            if not isinstance(child, Token):
                yield from child.nodes
            else:
                yield child

    cdef bool _is_terminal(self):
        return False

    @staticmethod
    def _from_list(tree, int index=0):
        if len(tree) == 2 and isinstance(tree[1], str):
            return Token(tree[1], tree[0], index=index)
        else:
            children = []
            for i,c in enumerate(tree[1:]):
                children.append(InternalNode._from_list(c, index=index+i))
            children = np.array(children, dtype=np.object_)
            return InternalNode(index, tree[0], children)

    def __repr__(self):
        return "<InternalNode %s>" % self.tag

cdef class Tree:
    cdef InternalNode root

    def __init__(self, InternalNode root):
        self.root = root

    @property
    def tokens(self):
        cdef Node node
        for node in self.nodes:
            if isinstance(node, Token):
                yield node

    @property
    def nodes(self):
        yield from self.root.nodes

    def __iter__(self):
        return self.tokens

    def __len__(self):
        return len(self.tokens)

    @staticmethod
    def from_list(tree):
        return Tree(InternalNode._from_list(tree))
