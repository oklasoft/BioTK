import numpy as np
cimport numpy as np

cdef class Node:
    cdef readonly:
        int index
        str tag

cdef class Token(Node):
    cdef readonly str word

    def __init__(self, str word, str tag=None, int index=-1):
        self.index = index
        self.word = word
        self.tag = tag

    def __repr__(self):
        return "%s/%s" % (self.word, self.tag)

cdef class InternalNode(Node):
    cdef object children

    def __init__(self, int index, str tag, 
            np.ndarray[dtype=object, ndim=1] children):
        self.index = index
        self.tag = tag
        self.children = children

    @property
    def tokens(self):
        cdef Node child
        for child in self.children:
            if isinstance(child, Token):
                yield child
            else:
                yield from child.tokens

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

cdef class Tree:
    cdef InternalNode root

    def __init__(self, InternalNode root):
        self.root = root

    @property
    def tokens(self):
        return list(self.root.tokens)

    def __iter__(self):
        return self.tokens

    def __len__(self):
        return len(self.tokens)

    @staticmethod
    def from_list(tree):
        return Tree(InternalNode._from_list(tree))
