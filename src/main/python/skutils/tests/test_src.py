#-*- encoding: utf8 -*-
__author__ = 'flappy'

import nose
from nose.tools import assert_raises

def test_realloc1():
    from sklearn.tree._utils import _realloc_test
    assert_raises(MemoryError, _realloc_test)

def test_realloc():
    from skutils.src.memUtil import _realloc_test
    assert_raises(MemoryError, _realloc_test)

if __name__ == '__main__':
    nose.runmodule()