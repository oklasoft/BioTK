cdef:
    enum Strand:
        STRAND_UNKNOWN = 0
        STRAND_FWD = 1
        STRAND_REV = 2

    cdef str strand_to_string(Strand strand)

    class Interval:
        cdef long start
        cdef long end
        cdef double score
        cdef Strand strand

    class Region:
        cdef readonly: 
            str contig
            long start, end
            str name
            double score
        cdef:
            Strand strand

        cpdef long length(Region self)
