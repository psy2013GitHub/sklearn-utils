#-*- encoding: utf8 -*-
__author__ = 'flappy'

#
# 可视化
#

import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import ward, dendrogram

class Text:

    @staticmethod
    def hc(linkage_matrix, labels, file):
        '''
            hierarchical clustering visualise
        :param dist:
        :return:
        '''
        fig, ax = plt.subplots(figsize=(15, 20)) # 设置大小
        ax = dendrogram(linkage_matrix, orientation="right", labels=labels)

        plt.tick_params(
                axis= 'x',          # 使用 x 坐标轴
                which='both',      # 同时使用主刻度标签（major ticks）和次刻度标签（minor ticks）
                bottom='off',      # 取消底部边缘（bottom edge）标签
                top='off',         # 取消顶部边缘（top edge）标签
            labelbottom='off')

        plt.tight_layout() # 展示紧凑的绘图布局
        if file is sys.stdout:
            plt.show()
        else:
            plt.savefig(file, dpi=200) # 保存图片为 ward_clusters


if __name__ == '__main__':
    import sys
    pass
