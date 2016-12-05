#-*- encoding: utf8 -*-
__author__ = 'flappy'

# 并查集 https://en.wikipedia.org/wiki/Disjoint-set_data_structure

class DisjoinSets:

    def __init__(self, length):
        self.array = [-1,] * length

    def find(self, x):
        '''
        :param x: 索引下标
        :return: 集合id
        '''
        assert x < len(self.array), '%s longer than max array length %d' % (str(x), len(self.array))
        if self.array[x] < 0:
            return x
        else:
            return self.find(self.array[x]) # recursive

    def union(self, s1, s2):
        '''
        :param s1: 集合1 id
        :param s2: 集合2 id
        :return:
        '''
        assert s1 < len(self.array) and s2 < len(self.array), '%s or %s longer than max array length %d' % (str(s1), str(s2), len(self.array))
        if s1 == s2:
            return

        if s1 < s2:
            self.array[s1] += self.array[s2]
            self.array[s2] = s1
        else:
            self.array[s2] += self.array[s1]
            self.array[s1] = s2

    def set_count(self, s):
        '''
        :param s: 集合id
        :return: 集合包含元素数量
        '''
        return self.array[s] * -1

def testDisjoinSets():
    inst = DisjoinSets(10)
    print 2, inst.find(2)
    print 'after union 2 & 3', inst.union(inst.find(2), inst.find(3)), 'now 3 belongs to set', inst.find(3)
    print 'after union 3 & 4', inst.union(inst.find(3), inst.find(4)), 'now 4 belongs to set', inst.find(4)

def testTreeDisjoinSets():
    pass

if __name__ == '__main__':
    testDisjoinSets()
    testTreeDisjoinSets()