#-*- encoding: utf8 -*-
__author__ = 'flappy'

import sys
reload(sys)
sys.setdefaultencoding('utf8')

DEBUG = False

def DPrint(format_str, *args):
    '''
        Debug Print
    '''
    global DEBUG
    if DEBUG:
        if len(args) > 0:
            print format_str % (args)
        else:
            print format_str


if __name__ == '__main__':
    DEBUG = False
    DPrint('%s, %d', 'no hello world', 2016)
    DEBUG = True
    DPrint('%s, %d', 'hello world', 2016)
