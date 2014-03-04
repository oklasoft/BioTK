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

cdef str strand_to_string(Strand strand):
    if strand == STRAND_FWD:
        return "+"
    elif strand == STRAND_REV:
        return "-"
    else:
        return "."

cdef class Region:
    cdef readonly: 
        str contig
        long start, end
        str name
        double score
    cdef:
        Strand strand

    property strand:
        def __get__(self):
            return strand_to_string(self.strand)

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

    def __repr__(self):
        return "<Region %s:%s-%s (%s)>" % (self.contig, self.start, self.end, 
                strand_to_string(self.strand))
