"""
Various types of indices for genomic intervals, both RAM and disk-based.
"""

cdef class IntervalNode:
    cdef object intervals
    cdef Interval

cdef class RAMIndex:
    def __init__(self, regions):

        
