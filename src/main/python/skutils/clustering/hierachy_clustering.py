#-*- encoding: utf8 -*-
from __future__ import division

__author__ = 'flappy'

import numpy as np
from utils.DisjoinSets import DisjoinSets

class HierarchyClustering:

    '''
        toy, just for fun
    '''

    def __init__(self, max_dist=None, max_clusters=None):
        pass

    def fit_x(self, X, dist_func=None):
        assert getattr(dist_func, '__call__', None), 'dist func not callable'
        n_points = len(X)
        dist_mat = self.calc_dist(X, dist_func)
        return self.fit_dist(dist_mat, n_points)

    def stop(self, curr_min_dist, curr_n_clusters, max_dist, max_n_clusters):
        if max_dist is None and curr_n_clusters >= max_n_clusters:
            return
        if max_n_clusters is None and curr_min_dist >= max_dist:
            return

    def fit_dist(self, dist_mat, n_points, max_dist=None, max_n_clusters=None):
        '''
            在聚类过程中，每个cluster可被认作是一个点，点到cluster使用DisoinSets索引
        :param dist_mat:
        :param n_points:
        :return:
        '''
        assert max_dist is None or max_n_clusters is None, 'arg error'
        n_clusters = n_points
        disjoinsets = DisjoinSets(n_points)
        while True:
            # 找到最短距离
            min_dist, mi, mj = None, None, None
            for i in range(n_points):
                for j in range(i, n_points):
                    if min_dist is None or dist_mat[i][j] < min_dist:
                        mi, mj, min_dist = i, j, dist_mat[i][j]

            # 判断是否满足退出条件
            if self.stop(min_dist, n_clusters, max_dist, max_n_clusters):
                return

            # 合并mi, mj两个cluster集合
            ci, cj = disjoinsets.find(mi), disjoinsets.find(mj)
            disjoinsets.union(ci, cj)

            # 重新计算距离矩阵
            dist_out, dist_inner = [None, ] * n_points, [np.inf, ] * n_points
            n1, n2 = disjoinsets.set_count(ci), disjoinsets.set_count(cj)
            for i in range(n_points): # 行
                d = (dist_mat[mi] * n1 + dist_mat[mj] * n2) / (n1 + n2)
                d = d if d!=0 else np.inf
                dist_out[i] = d # cluster与其他cluster(有可能是点)距离
                dist_inner[i] = np.inf # cluster内部距离，设置为无穷大
            for i in range(n_points):
                dist_mat[i][mi] = dist_mat[mi][i] = dist_out[i]
                dist_mat[i][mj] = dist_mat[mj][i] = dist_inner[i]

            # 更新状态信息
            n_clusters -= 1

    def calc_dist(self, X, dist_func):
        assert getattr(dist_func, '__call__', None), 'dist func not callable'
        n_clusters = n_points = len(X)
        dist_mat = [[None, ] * n_points, ] * n_points
        for i in range(n_points):
            for j in range(i, n_points):
                dist_mat[i][j] = dist_mat[j][i] = dist_func(X[i], X[j])
        return dist_mat