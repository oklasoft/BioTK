import sys

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

    def __richcmp__(Region self, Region o, int op):
        if op == 0: # <
            if self.contig < o.contig:
                return True
            elif (self.contig == o.contig):
                if self.start < o.start:
                    return True
                elif (self.start == o.start):
                    return self.end < o.end
            return False
        elif op == 2: # ==
            return (self.contig == o.contig) and \
                (self.start == o.start) and \
                (self.end == o.end)
        elif op == 4: # >
            return o.__richcmp__(self, 0)
        elif op == 1: # <=
            return not self.__richcmp__(o, 4)
        elif op == 3: # !=
            return not self.__richcmp__(o, 2)
        elif op == 5: # >=
            return not self.__richcmp__(o, 0)
