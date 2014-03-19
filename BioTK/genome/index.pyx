"""
Various types of indices for genomic regions, both RAM and disk-based.
"""

from itertools import groupby
from operator import attrgetter

from cpython cimport bool

from BioTK.genome.region cimport Region

cdef class Node:
    cdef Region payload
    cdef Node left, right
    cdef int max_end

    def __init__(self, list regions):
        midpoint = int(len(regions) / 2)
        self.payload = regions[midpoint]
        self.max_end = self.payload.end
        if midpoint > 0:
            self.left = Node(regions[:midpoint])
            self.max_end = max(self.max_end, self.left.max_end)
        if midpoint < len(regions) - 1:
            self.right = Node(regions[(midpoint+1):])
            self.max_end = max(self.max_end, self.right.max_end)

    def search(self, list result, int start, int end):
        if start > self.max_end:
            return
        if self.left:
            self.left.search(result, start, end)
        if (start < self.payload.end) and (end > self.payload.start):
            result.append(self.payload)
        if end < self.payload.start:
            return
        if self.right:
            self.right.search(result, start, end)

cdef class RAMIndex:
    """
    A RAM-based index for (generic) intervals.
    
    This is a simple augmented binary search tree as described
    in CLRS 2001.
    """
    cdef readonly:
        object _regions
        object _roots
        bool _built

    def __init__(self):
        """
        A RAM-based index for genomic regions on multiple chromosomes/contigs.
        """
        self._regions = []
        self._roots = {}
        self._built = False

    def add(self, Region r):
        """
        Add another region to the index. This method can only be
        called if the index has not been built yet.
        """
        if self._built:
            msg = "Can't currently mutate a constructed RAMIndex."
            raise Exception(msg)
        self._regions.append(r)

    def build(self):
        """
        Build the index. After this method is called, new intervals
        cannot be added.
        """
        self._regions.sort()
        for contig, regions in groupby(self._regions, attrgetter("contig")):
            self._roots[contig] = Node(list(regions))
        self._built = True

    def search(self, str contig, int start, int end):
        """
        Search the index for intervals overlapping the given 
        contig, start, and end.
        """
        assert(self._built)
        start, end = sorted([start, end])
        if not self._built:
            raise Exception("Must call %s.build() before using search()" % \
                            str(type(self)))
        root = self._roots.get(contig)
        result = []
        if root is not None:
            root.search(result, start, end)
        return result

    def __iter__(self):
        assert(self._built)
        return iter(self._regions)
