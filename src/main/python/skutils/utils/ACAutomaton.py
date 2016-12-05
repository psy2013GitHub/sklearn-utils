#-*- encoding: utf8 -*-
__author__ = 'root'

from Queue import Queue
from utils.verbose import DPrint

class ACAutomatonNode(object):

    def __init__(self, depth=0, next=None, fail=None, val=None):
        self.next = {} if next is None else next # 指向前面节点 {val: Node(val), ...}
        self.fail = fail # 表示下一个字符匹配不了时，接盘节点，可知，一定是同val节点
        self.val = val  # 当前节点保存的值
        self.word_idx = None
        self.depth = depth

class ACAutomaton(object):
    '''
     形成AC自动机
     !!! 输入必须是unicode
    '''
    def __init__(self, pats=None, sep=None):
        self.root = ACAutomatonNode()
        self.root.fail = None
        self.curr_word_idx = 0
        if not(pats is None) and len(pats) > 0:
            for pat in pats:
                pat = pat.strip()
                usep = None
                if not(sep is None):
                    usep = sep.decode('utf8')
                self.add(pat.decode('utf8'), usep)
            self.set_fail()

    def add(self, word, sep=None):
        assert len(word) > 0, 'len(%s) must not be 0' % word
        assert sep is None or isinstance(sep, unicode)
        assert isinstance(word, unicode)
        if not sep:
            chars = [_ for _ in word if _ and len(_) > 0]
        else:
            chars = [_ for _ in word.split(sep) if _ and len(_) > 0]
            # print word, '    ', ','.join(chars)
        curr = self.root
        new_edge = False
        for c in chars:
            # print 'c:', c
            # if c == '3p':
            #     print '3p-----------------------'
            DPrint('add: curr: %s %s', c, curr.val)
            if not(c in curr.next): # 如果没有前进点，new 跳过
                curr.next[c] = ACAutomatonNode(val=c, depth=curr.depth+1)
                DPrint('        +: %s %s', c, ','.join(curr.next.keys()))
                new_edge = True
            curr = curr.next[c]
        if new_edge:
            curr.word_idx = self.curr_word_idx
            self.curr_word_idx += 1
        else:
            if self.is_word_end(curr):
                print "warning: insert a already existed key %s" % word
            else:
                curr.word_idx = self.curr_word_idx
                self.curr_word_idx += 1
        # if len(chars)==1  and chars[0] == '3p':
        #     print 'add: final: %s %d', curr.val, curr.word_idx
        DPrint('add: final: %s %d', curr.val, curr.word_idx)

    def set_fail(self):
        if self.curr_word_idx == 0:
            return
        # bfs 算法，保证最大后缀对应最长根前缀
        Q = Queue(self.root)
        depth = 1
        while not Q.is_empty():
            p = Q.pop()
            if not p.next:
                DPrint('set_fail: empty next: %s ', p.val)
                continue

            DPrint('set_fail: childs: %s', ','.join(p.next.keys()))
            for c, child in p.next.items():
                DPrint('set_fail: curr: %s', c)
                # 关键点1是如何确定root.child.fail
                fail = p.fail
                while fail:
                    DPrint('set_fail: while: %s %d %s %d', c, child.depth, p.val, p.depth)
                    if fail.next.has_key(c):
                        child.fail = fail.next[c]
                        DPrint('set_fail: in: %s %d %s %d', c, child.depth, child.fail.val, child.fail.depth)
                        break
                    else:
                        fail = fail.fail
                if fail is None:
                    child.fail = self.root
                    DPrint('set_fail: root: %s %d %s %d', c, child.depth, child.fail.val, child.fail.depth)
                DPrint('set_fail: push: %s', c)
                Q.push(child) # 加入Q
            depth += 1

    def bfs_traverse(self):
        Q = Queue(self.root)
        while not Q.is_empty():
            p = Q.pop()
            if not p.next:
                continue

            print ','.join(p.next.keys())
            for c, child in p.next.items():
                DPrint('set_fail: push: %s %d %s %d', c, child.depth, child.fail.val, child.fail.depth)
                Q.push(child) # 加入Q

    def is_word_end(self, node):
        return not(node is None or node.word_idx is None)

    def query(self, chars):
        # 返回第一个不匹配位置
        # 每次对比next
        idxs = []
        prev, curr = None, self.root
        i = 0
        while i < len(chars):
            c = chars[i]
            DPrint('query: curr: %s', c)
            if self.is_word_end(curr):
                idxs.append(curr.word_idx)
            if curr.next.has_key(c):
                DPrint('query: hit: %s', c)
                curr = curr.next[c]
                i += 1
            elif curr.fail:
                # if not(curr.fail is self.root):
                #      if curr.word_idx:
                #         idxs.append(curr.word_idx)
                # print idxs
                DPrint('query: fail: %s %s', curr.val, curr.fail.val)
                curr = curr.fail
            else:
                i += 1
        if self.is_word_end(curr):
            idxs.append(curr.word_idx)
        while curr and not(curr.fail is self.root): # !!! necessary, for case, words=['不见面了', '见面了', '面了', '了'], query=['不见面了']
            curr = curr.fail
            if self.is_word_end(curr):
                DPrint('query: tail: %s %s %s', curr.val, curr.word_idx, curr.fail.val)
                idxs.append(curr.word_idx)
        return idxs # 返回 0 或 长度

def test_automaton1():
    print '-' * 5, 'test_automaton', '-' * 5
    inst = ACAutomaton()
    inst.add('你好'.decode('utf8'))
    inst.add('不见'.decode('utf8'))
    inst.add('不见面'.decode('utf8'))
    inst.add('你快来'.decode('utf8'))
    inst.add('见面'.decode('utf8'))
    inst.set_fail()
    # inst.bfs_traverse()
    print inst.query("美女sayhi".decode('utf8'))
    print inst.query("你好".decode('utf8'))
    print inst.query("不见".decode('utf8'))
    print inst.query("不见面".decode('utf8'))
    print inst.query("你快来".decode('utf8'))
    print inst.query("见面".decode('utf8'))
    print inst.query("美女我想你你快来你快来见面见啊面见面".decode('utf8'))
    print inst.query("美女不见你你快来你快来见面见啊面见面".decode('utf8'))
    print inst.query("美女不见你你快来你快来不见面不见面".decode('utf8'))

def test_automaton2():
    print '-' * 5, 'test_automaton', '-' * 5
    inst = ACAutomaton()
    inst.add('快乐'.decode('utf8'))
    inst.add('的'.decode('utf8'))
    inst.add('的3'.decode('utf8'))
    inst.add('3天'.decode('utf8'))
    inst.set_fail()
    # inst.bfs_traverse()
    fail = inst.root.next['的'.decode('utf8')].next['3'].fail
    print fail.val, fail.next.keys()
    print inst.query("美女sayhi".decode('utf8'))
    print inst.query("快乐".decode('utf8'))
    print inst.query("的".decode('utf8'))
    print inst.query("的3".decode('utf8'))
    print inst.query("3天".decode('utf8'))
    print inst.query('快乐的3天'.decode('utf8'))

if __name__ == '__main__':
    test_automaton2()


    # print inst.query('不见面'.decode('utf'))