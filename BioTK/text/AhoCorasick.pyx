from cpython cimport bool

# TODO: handle overlaps
# TODO: possibly use a STL map and pointers 
#   to get better performance for searches?

cdef class Match:
    cdef readonly:
        int start, end
        object key

    def __cinit__(self, start, end, key=None):
        self.start = start
        self.end = end
        self.key = key

cdef class Node:
    cdef public:
        int depth
        object key
        bool terminal
        dict children
        Node fail

    def __cinit__(self, int depth=0):
        self.terminal = False
        self.children = {}
        self.depth = depth

    def search(self, Py_UCS4 c):
        if <int> c in self.children:
            return self.children[<int> c]
        elif self.depth == 0:
            return self
        else:
            return self.fail.search(c)

    def search_without_fail_transition(self, Py_UCS4 c):
        return self.children.get(<int> c, self)

def _add_fail_transitions(node):
    for c,child in node.children.items():
        child.fail = node.fail.search_without_fail_transition(c)

    for child in node.children.values():
        _add_fail_transitions(child)

cdef class Trie:
    cdef:
        Node root
        bool built, case_sensitive, allow_overlapping

    def __init__(self, case_sensitive=True, allow_overlapping=True):
        self.root = Node()
        self.built = False
        self.case_sensitive = case_sensitive

    def add(self, str text, key=None):
        if self.built:
            raise Exception("Cannot add a new search term to a built Trie.")
        if not self.case_sensitive:
            text = text.lower()
        cdef Node node = self.root
        cdef Py_UCS4 c
        while text:
            c = text[0]
            if not <int> c in node.children:
                node.children[<int> c] = Node(depth=node.depth+1)
            node = node.children[<int> c]
            text = text[1:]
        node.terminal = True
        node.key = key

    def build(self):
        self.root.fail = self.root
        for child in self.root.children.values():
            child.fail = self.root
        for child in self.root.children.values():
            _add_fail_transitions(child)
        self.built = True

    def search(self, str text):
        if not self.case_sensitive:
            text = text.lower()
        cdef Py_UCS4 c
        cdef Node node = self.root
        cdef Node n
        matches = []
        for i,c in enumerate(text):
            node = node.search(c)
            if node.terminal:
                n = node
                while n.terminal:
                    matches.append(Match(1 + i - n.depth, i + 1, node.key))
                    n = n.fail
        return matches

class MixedCaseSensitivityTrie(object):
    def __init__(self, allow_overlaps=True):
        self._cs = Trie(case_sensitive=True)
        self._ci = Trie(case_sensitive=False)

    def build(self):
        self._cs.build()
        self._ci.build()
    
    def add(self, str text, bool case_sensitive=False, object key=None):
        trie = self._cs if case_sensitive else self._ci
        trie.add(text, key=key)

    def search(self, str text):
        return self._cs.search(text) + self._ci.search(text)
