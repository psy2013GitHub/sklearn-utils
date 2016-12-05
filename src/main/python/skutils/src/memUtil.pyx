
from libc.stdlib cimport free
from libc.stdlib cimport malloc
from libc.stdlib cimport realloc

import numpy as np
cimport numpy as np
np.import_array()

cdef realloc_ptr save_realloc_vec(realloc_ptr* ptr, size_t size) except *:
    if ptr == NULL and size == 0:
        return NULL
    if size == 0:
        return ptr[0]
    # check overflow
    cdef size_t bytes = size * sizeof(ptr[0][0])
    if bytes / size != sizeof(ptr[0][0]):
        raise MemoryError("overflow in (%d * %d) bytes" % (sizeof(ptr[0][0]), size))
    # realloc & check
    cdef realloc_ptr new_ptr = <realloc_ptr>realloc(ptr[0], bytes)
    if new_ptr == NULL:
        raise MemoryError("cannot realloc %d bytes" % bytes)
    ptr[0] = new_ptr

    return new_ptr

def _realloc_test():
    cdef SIZE_t* p = NULL
    save_realloc_vec(&p, <size_t>(-1)/2)
    if p != NULL:
        free(p)
        assert False