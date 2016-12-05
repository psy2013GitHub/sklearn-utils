#-*- encoding: utf8 -*-
# __author__ = 'flappy'

import numpy as np
cimport numpy as np

ctypedef np.npy_float32 DTYPE_t
ctypedef np.npy_float64 DOUBLE_t
ctypedef np.npy_intp SIZE_t
ctypedef np.npy_int32 INT32_t
ctypedef np.npy_uint32 UINT32_t

ctypedef fused realloc_ptr:
    (DTYPE_t*)
    (SIZE_t*)
    (unsigned char*)

cdef realloc_ptr save_realloc_vec(realloc_ptr* ptr, size_t size) except * # 为什么这里ptr用**指针，可以理解为直接修改指针

# cdef _realloc_test():


