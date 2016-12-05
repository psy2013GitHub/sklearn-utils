#-*- encoding: utf8 -*-
# @ref: http://blog.csdn.net/dm_ustc/article/details/45565921
__flappy__ = 'dz'

import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.ensemble.weight_boosting import AdaBoostClassifier
from tree.translator import TreeTranslator
from lab.utils.random import shuffle

class TreeLR(object):

    def __init__(self, method, n_trees, **kargs):
        self.method = str.lower(method)
        self.n_trees = n_trees
        self.estimators = [None,] * n_trees
        self.kargs = kargs
        self.nodeIdx2leafIdxDict = None

        assert self.method in ['rf', 'ada'], NotImplementedError(method)

    def fit1(self, X, Y, export_tree=False):
        # step 1, fit for tree
        if self.method == 'rf':
            for i in range(self.n_trees):
                print '-' * 10 , 'tree: %d' % i , '-' * 10
                # 准备数据
                shuffle(X, Y)
                tree = DecisionTreeClassifier(**self.kargs)
                tree.fit(X, Y)
                if export_tree:
                    export_graphviz(tree, 'tree_%d.dot' % i)

                self.estimators[i] = TreeTranslator(tree.tree_, tree.n_outputs_, tree.classes_)

        elif self.method == 'ada':
            base = DecisionTreeClassifier(**self.kargs)
            ada = AdaBoostClassifier(n_estimators=self.n_trees, base_estimator=base)
            ada.fit(X, Y)
            self.estimators = [TreeTranslator(est.tree_, est.n_outputs_, est.classes_) for est in ada.estimators_]

    def augX(self, X):
        '''
            依据决策树结果对叶子节点进行增广
        :param est_list:
        :param X:
        :param augLen:
        :return:
        '''
        if not self.nodeIdx2leafIdxDict:
            nodeIdx2leafIdxDict = [None,] * self.n_trees
            self.aug_len = 0
            for i, e in enumerate(self.estimators):
                self.nodeIdx2leafIdxDict[i], x2 = e.nodeIdx2leafIdx()[0]
                self.aug_len += x2
        res = np.zeros([X.shape[0], X.shape[1] + self.aug_len])
        for i, x in enumerate(X):
            res[i, :len(x)] = x
            for j, est in enumerate(self.estimators):
                # print est.lChilds
                idx = est.sample2nodeIdx(x)
                tmp = self.nodeIdx2leafIdxDict[j]
                # print idx
                idx = tmp[idx]
                res[i, idx] = 1 # sparse encoding
        return res


    def to_be_continue(self):
        pass