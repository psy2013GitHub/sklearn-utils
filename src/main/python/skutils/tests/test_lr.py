
#-*- encoding: utf8 -*-
from __future__ import division

__author__ = 'flappy'

import numpy as np
from functools import partial
from linear.logistic_regression import LR, NaiveLR

def loadXY(fid):
    X, Y, u_lables = [], [], set()
    for line in fid.readlines():
        line = line.strip()
        if len(line) == 0:
            continue
        segs = line.strip().split('\t')
        X.append([float(segs[i]) for i in range(21)])
        y = int(float(segs[21]))
        u_lables.add(y)
        y = -1 if y <= 0 else 1
        Y.append(y)
    X, Y = np.array(X), np.array(Y)
    assert np.isnan(X).sum() == 0 and np.isnan(Y).sum() == 0, 'load data: nan error'
    assert len(u_lables)==2 and 0 in u_lables and 1 in u_lables, 'load data, file check: 0/1 code'
    return X, Y

def get_constraints(n_features, n_pos_features):
    cons = []
    def f1(idx):
        return lambda x: np.array([x[idx] - 0.00])
    def jac1(idx):
        tmp = np.zeros(n_features+1)
        tmp[idx] = 1.0
        return lambda x: tmp
    def f2(idx):
        return lambda x: np.array([0.00 - x[idx]])
    def jac2(idx):
        tmp = np.zeros(n_features+1)
        tmp[idx] = -1.0
        return lambda x: tmp
    for _ in range(n_features):
        tmp = np.zeros(n_features+1) # +1 别忘了斜率
        if _ < n_pos_features:
            tmp[_] = 1.0
            cons.append({
            'type': 'ineq',
            'fun' : f1(_),
            'jac' : jac1(_),
            })
        else:
            tmp[_] = -1.0
            cons.append({
            'type': 'ineq',
            'fun' : f2(_),
            'jac' : jac2(_),
            })

    # for _ in range(n_features):
    #     tmp = np.zeros(n_features+1); tmp[_] = 1
    #     print 'cons:', cons[_]['fun'](tmp), cons[_]['jac'](tmp)
    return cons


def colicTest(method='sklearn', solver=None, alpha=0.1, use_constraints=False):
    frTrain = open('../data/colic/horseColicTraining.txt'); frTest = open('../data/colic/horseColicTest.txt')
    X, Y = loadXY(frTrain)
    print X.shape, Y.shape
    print 'X[1]', ','.join(str(_) for _ in X[1])

    n_features = X.shape[1]
    n_pos_features = int(X.shape[1] / 2)

    constraints = tuple(get_constraints(n_features, n_pos_features)) if use_constraints else []
    options={'maxiter': 100000, 'disp': True}

    if method == 'sklearn':
        if not(constraints is None):
            print 'Warning: constraints is not available in sklearn'
        sigmoid_method, logsum_method =None, None
        lr = LR()
        lr.fit(X, Y, alpha=alpha, solver=solver, options=options)
        predict_func = lr.predict
        predict_proba_func = lr.predict_proba
    elif method == 'local':
        sigmoid_method, logsum_method = 'fabian_stable', 'fabian_stable'
        lr = NaiveLR(sigmoid_method=sigmoid_method, logsum_method=logsum_method,)
        trainWeights = lr.fit(X, Y, alpha=alpha,
                          constraints=constraints, solver=solver, options=options,
        )
        print 'theta:', trainWeights
        predict_func = partial(lr.predict, sigmoid_method=sigmoid_method)
        predict_proba_func = partial(lr.predict_proba, sigmoid_method=sigmoid_method)
        predict_proba_func = lr._predict_proba_lr
    else:
        raise NotImplementedError('%s' % method)

    predict = predict_func(X)
    print predict_proba_func(X)
    cCnt = np.sum(predict > 0)
    acc = cCnt/len(Y)
    print "the accuracy of this train is: %f" % acc

    X, Y = loadXY(frTest)
    predict = predict_func(X)
    cCnt = np.sum(predict > 0)
    acc = cCnt/len(Y)
    print "the accuracy of this test is: %f" % acc

def testPartial():
    f = lambda x1, x2: x1 + x2
    f1 = partial(f, 3)
    assert f(1, 3) == f1(1) == 4

def testClosure():
    fs = []
    def f(idx):
        return lambda x: idx
    for _ in range(10):
        fs.append(f(_))
    for _ in range(10):
        print fs[_](1)


if __name__ == '__main__':
    # testPartial()
    colicTest(method='local', solver='SLSQP', alpha=0.001)
    # testClosure()

'''
    1, naive方法容易overflow
    2, 仅仅使用Sigmoid.stable不足以解决数值问题
    4, 'fabian_stable' 或 'sklearn计算loss & grad方法' 靠谱
'''
