#-*- encoding: utf8 -*-
__author__ = 'flappy'

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os

def load_text(fname, weight=1, preprocessor_func=None, filter_func=None):
    '''
    :param fname: 文件名
    :param weight: 文件样本权重
    :param preprocessor_func: 预处理函数
    :param filter_func: 过滤函数
    :return:
    '''

    if not os.path.exists(fname):
        print 'error: %s not exist' % fname
        return

    use_preprocessor_func = True if preprocessor_func and getattr(preprocessor_func, '__call__', None) else False

    with open(fname) as fid:
        res = []
        for line in fid:
            # tmp = line.rsplit('\tT', 1)
            tmp = line.strip()
            if len(tmp) > 0:
                if filter_func and filter_func(tmp):
                    continue
                if weight > 0:
                    for _ in range(int(weight)):
                        res.append(tmp)
    for i, text in enumerate(res):
        if use_preprocessor_func:
            text = preprocessor_func(text) # 替换java预处理部分tag
        res[i] = text

    return res