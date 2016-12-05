#-*- encoding: utf8 -*-
__author__ = 'flappy'

import numpy as np

def shuffle(*args, **kargs):
    seed = kargs.get('seed', 253759639)
    for arg in args:
        x1 = arg[0]
        np.random.seed(seed)
        np.random.shuffle(arg)
        x2 = arg[0]
        print 'x1:', x1, 'x2:',


if __name__ == '__main__':
    x1, x2 = [1,2,3], [4,5,6]
    shuffle([x1, x2])
    print x1, x2