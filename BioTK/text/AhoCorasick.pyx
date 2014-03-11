from cpython cimport bool

# TODO: possibly use a STL map and pointers 
#   to get better performance for searches?

__all__ = ["Trie", "MixedCaseSensitivityTrie"]

def longest_nonoverlapping_matches(matches):
    out = []
    cdef Match m1, m2
    cdef bool ok
    matches.sort(key=len).reverse()
    for m1 in matches:
        ok = True
        for m2 in out:
            if m1.overlaps(m2):
                ok = False
        if ok:
            out.append(m1)
    return out

def restrict_by_boundary_characters(matches, str query, str bchars):
    out = []
    for m in matches:
        if not ((m.start == 0) or (query[m.start - 1] in bchars)):
            continue
        if not ((m.end == len(query)) or (query[m.end] in bchars)):
            continue
        out.append(m)
    return out

cdef class Match:
    cdef readonly:
        int start, end
        object key

    def __cinit__(self, start, end, key=None):
        self.start = start
        self.end = end
        self.key = key

    def __len__(self):
        return self.end - self.start

    cdef bool overlaps(self, Match o):
        return self.end > o.start and self.start < o.end

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
        bool built, case_sensitive, allow_overlaps
        str boundary_characters

    def __init__(self, 
            case_sensitive=True, 
            allow_overlaps=True,
            boundary_characters=""):
        """
        Create a keyword Trie.

        Parameters
        ----------

        case_sensitive : bool, optional
        allow_overlaps : bool, optional
            Whether to allow overlapping matches or not.
            If not, the longest nonoverlapping matches are returned.
        boundary_characters : str, optional
            If provided, matches are required to be bounded on both sides 
            by one of the given characters, or by the query string beginning
            or end.
        """
        self.root = Node()
        self.built = False
        self.case_sensitive = case_sensitive
        self.allow_overlaps = allow_overlaps
        self.boundary_characters = boundary_characters

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
        if self.boundary_characters:
            matches = restrict_by_boundary_characters(
                    matches, text, self.boundary_characters)
        if not self.allow_overlaps:
            matches = longest_nonoverlapping_matches(matches)
        return matches

class MixedCaseSensitivityTrie(object):
    def __init__(self, allow_overlaps=True, boundary_characters=""):
        self._cs = Trie(case_sensitive=True, 
                boundary_characters=boundary_characters,
                allow_overlaps=True)
        self._ci = Trie(case_sensitive=False, 
                boundary_characters=boundary_characters,
                allow_overlaps=True)
        self.allow_overlaps = allow_overlaps

    def build(self):
        self._cs.build()
        self._ci.build()
    
    def add(self, str text, bool case_sensitive=False, object key=None):
        trie = self._cs if case_sensitive else self._ci
        trie.add(text, key=key)

    def search(self, str text):
        matches = self._cs.search(text) + self._ci.search(text)
        if not self.allow_overlaps:
            matches = longest_nonoverlapping_matches(matches)
        return matches
