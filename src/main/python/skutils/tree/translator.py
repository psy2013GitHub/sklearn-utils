#-*- encoding: utf8 -*-

__author__ = 'deng.zhou'

import numpy as np
from sklearn.tree._tree import TREE_LEAF, TREE_UNDEFINED

class TreeTranslator(object):

    def __init__(self, clf, n_outputs, classes):
        self.lChilds = clf.children_left
        self.rChilds = clf.children_right
        self.feature = clf.feature
        self.threshold = clf.threshold
        self.value = clf.value

        self.n_outputs = n_outputs
        self.classes = classes
        self.n_classes = len(self.classes)

    def predict_raw_proba(self, x, idx=0, return_node_idx=False):
        leaf_idx = -1 # 叶子节点下标
        i = 0
        while True:
            curr_feature = self.feature[i]
            curr_thresh = self.threshold[i]
            # if idx==1256:
            #     print i
            #     print curr_feature
            #     print curr_thresh
            if curr_feature == TREE_UNDEFINED or curr_thresh == TREE_UNDEFINED:
                leaf_idx = i
                break
            if x[curr_feature] <= curr_thresh:
                j = self.lChilds[i]
                if j == TREE_LEAF:
                    leaf_idx = i
                    break
                i = j
            else:
                j = self.rChilds[i]
                if j == TREE_LEAF:
                    leaf_idx = i
                    break
                i = j
        p = self.value[i]
        if return_node_idx:
            return p, leaf_idx
        return p

    def predict_proba(self, x, idx=0):
        p = self.predict_raw_proba(x, idx=idx)
        if self.n_outputs == 1:
            proba = p[:, :self.n_classes]
            normalizer = proba.sum(axis=1)[:, np.newaxis]
            normalizer[normalizer == 0.0] = 1.0
            proba /= normalizer
            return proba

        else:
            all_proba = []
            for k in range(self.n_outputs):
                proba_k = p[:, k, :self.n_classes[k]]
                normalizer = proba_k.sum(axis=1)[:, np.newaxis]
                normalizer[normalizer == 0.0] = 1.0
                proba_k /= normalizer
                all_proba.append(proba_k)
            return all_proba

    def predict(self, x):
        p = self.predict_raw_proba(x)
        y = []
        if self.n_outputs > 1:
            for k in range(self.n_outputs):
                y.append(self.classes[k].take(np.argmax(p[k, :]), axis=0))
        else:
            y = self.classes.take(np.argmax(p[0, :]), axis=0)
        return y

    def nodeIdx2leafIdx(self):
        '''
            每个节点对应第几个叶子节点，－1为内部节点
        :return:
        '''
        res = {i:-1 for i in range(len(self.feature))}
        idx = 0
        for i in range(len(self.lChilds)):
            if self.lChilds[i] == TREE_LEAF:
                res[i] = idx
                idx += 1
        return res, idx+1 # idx+1表示叶子节点个数

    def sample2nodeIdx(self, x):
        p, node_idx = self.predict_raw_proba(x, return_node_idx=True)
        return node_idx

    def dump(self, fname, header=None):
        with open(fname, 'wb') as fid:
            if header and isinstance(header, str):
                fid.write(header)
            fid.write('\n# n_nodes\n')
            fid.write(str(len(self.feature)))
            fid.write('\n# n_outputs\n')
            fid.write(str(self.n_outputs))
            fid.write('\n# n_classes\n')
            fid.write(str(len(self.classes)))
            fid.write('\n# classes\n')
            fid.write(','.join([str(i) for i in self.classes]))
            fid.write('\n# TREE_LEAF\n')
            fid.write(str(TREE_LEAF))
            fid.write('\n# TREE_UNDEFINED\n')
            fid.write(str(TREE_UNDEFINED))
            fid.write('\n# lChilds\n')
            fid.write(','.join([str(i) for i in self.lChilds]))
            fid.write('\n# rChilds\n')
            fid.write(','.join([str(i) for i in self.rChilds]))
            fid.write('\n# feature\n')
            fid.write(','.join([str(i) for i in self.feature]))
            fid.write('\n# threshold\n')
            fid.write(','.join([str(i) for i in self.threshold]))
            fid.write('\n# value\n')
            for node in self.value:
                for output in node:
                    fid.write(','.join([str(i) for i in output]) + '\n') # max_classes
