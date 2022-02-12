from libc.stdlib cimport malloc


cpdef unsigned char * CPCheckSum(unsigned char *content, unsigned long contentSize, unsigned char checksumSize):
    cdef unsigned long i
    cdef unsigned char n
    cdef unsigned char * checksum = <unsigned char *> malloc(checksumSize)

    for i in range(contentSize):
        for n in range(checksumSize):
            checksum[n] += content[i] if n == 0 else checksum[n-1]

    return checksum
