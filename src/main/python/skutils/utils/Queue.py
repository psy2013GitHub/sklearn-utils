#-*- encoding: utf8 -*-
__author__ = 'flappy'

from utils.verbose import DPrint

class QueueNode:

    def __init__(self, val=None, next=None):
        self.val = val
        self.next = next

class Queue(object):

    def __init__(self, val):
        self.queue = QueueNode(val)
        self.tail = self.queue
        self.length = 1

    def __len__(self):
        return self.length

    def is_empty(self):
        return self.queue is None

    def push(self, val):
        self.length += 1
        if self.is_empty():
            self.queue = QueueNode(val)
            self.tail = self.queue
        else:
            self.tail.next = QueueNode(val)
            self.tail = self.tail.next

    def pop(self):
        if self.is_empty():
            return
        self.length -= 1
        res = self.queue.val
        self.queue = self.queue.next
        return res

def test_queue():
    print '-' * 5, 'test_queue', '-' * 5
    import Random
    Q = Queue(1)
    Q.push(2)
    print Q.pop(), len(Q)
    print Q.pop(), len(Q)
    print Q.pop(), len(Q)
    Q.push(3)
    print Q.pop(), len(Q)
    print Q.is_empty()

    Q = Queue(1)
    for _ in range(20):
        x = Random.randint(0, 10)
        print 'push:', x
        Q.push(x)
    while not Q.is_empty():
        q = Q.pop()
        print 'get:', q

if __name__ == '__main__':
    test_queue()
