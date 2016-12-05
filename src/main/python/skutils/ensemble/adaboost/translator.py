#-*- encoding: utf8 -*-
__author__ = 'flappy'

import os
import numpy as np
from sklearn.tree import DecisionTreeClassifier

from python.tree.translator import TreeTranslator

class AdaTranslator(object):

    def __init__(self, clf):
        self.n_classes = clf.n_classes_
        self.classes = clf.classes_
        self.algorithm = clf.get_params()['algorithm']
        self.estimator_weights = clf.estimator_weights_
        if isinstance(clf.get_params()['base_estimator'], DecisionTreeClassifier):
            self.estimators = []
            self.classes = clf.estimators_[0].classes_
            for tree in clf.estimators_:
                self.estimators.append(TreeTranslator(tree.tree_, tree.n_outputs_, tree.classes_))
        else:
            raise NotImplementedError

    def predict_proba(self, x):
        if self.algorithm == 'SAMME.R':
            # The weights are all 1. for SAMME.R
            p = 0.0
            for i, estimator in enumerate(self.estimators):
                tmp = self._samme_proba(estimator, self.n_classes, x, i=i)
                # print '[', tmp[0][0], ',', tmp[0][1], ']', ','
                p += tmp
        else:   # self.algorithm == "SAMME"
            raise NotImplementedError

        # print p

        p /= self.estimator_weights.sum()
        p = np.exp((1. / (self.n_classes - 1)) * p)
        normalizer = p.sum(axis=1)[:, np.newaxis]
        normalizer[normalizer == 0.0] = 1.0
        p /= normalizer
        return p

    def _samme_proba(self, estimator, n_classes, X, i=0):
        proba = estimator.predict_proba(X, i)
        # if i==1256:
        #     print i, proba
        self.proba_dtype = proba.dtype
        # Displace zero probabilities so the log is defined.
        # Also fix negative elements which may occur with
        # negative sample weights.
        eps = self.np_eps(proba.dtype)
        proba[proba < eps] = eps
        log_proba = np.log(proba)

        return (n_classes - 1) * (log_proba - (1. / n_classes)
                              * log_proba.sum(axis=1)[:, np.newaxis])

    def np_eps(self, dtype):
        # fixme
        return np.finfo(dtype).eps

    def dump(self, directory):
        n_estimators = len(self.estimators)
        status = os.mkdir(directory)
        # 写header
        header_fpath = directory + os.path.sep + 'header'
        with open(header_fpath, 'w') as fid:
            fid.write('# algorithm\n')
            fid.write(self.algorithm)
            fid.write('\n# estimator_weights\n')
            fid.write(','.join([str(i) for i in self.estimator_weights]))
            fid.write('\n# np_eps\n')
            fid.write(str(self.np_eps(self.proba_dtype)))
            fid.write('\n# classes\n')
            fid.write(','.join([str(i) for i in self.classes]))
        # 写estimator
        for i, estimator in enumerate(self.estimators):
            fpath = directory + os.path.sep + 'estimator_%d' % i
            estimator.dump(fpath)
