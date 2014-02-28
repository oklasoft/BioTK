import sys

cdef:
    enum Strand:
        STRAND_UNKNOWN = 0
        STRAND_FWD = 1
        STRAND_REV = 2

    class Interval:
        cdef long start
        cdef long end
        cdef double score
        cdef Strand strand

cdef Strand parse_strand(str strand):
    if strand == "+":
        return STRAND_FWD
    elif strand == "-":
        return STRAND_REV
    else:
        return STRAND_UNKNOWN

cdef class Region:
    cdef: 
        str contig
        long start, end
        str name
        double score
        Strand strand

    def __init__(self, 
            str contig, long start, long end, 
            str name="",
            double score=0,
            str strand="."):
        self.contig = sys.intern(contig)
        self.start = start
        self.end = end
        self.name = sys.intern(name)
        self.strand = parse_strand(strand)

    cpdef long length(self) except *:
        return self.end - self.start

    def __len__(self):
        return self.length()
