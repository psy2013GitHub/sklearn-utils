#-*- encoding: utf8 -*-
__author__ = 'flappy'

import os
import sys
import subprocess
import numpy
from numpy.distutils.misc_util import Configuration

def generate_cython():
    cwd = os.path.abspath(os.path.dirname(__file__))
    print("Cythonizing sources")
    p = subprocess.call([sys.executable, os.path.join(cwd,
                                                      'build_tools',
                                                      'cythonize.py'),
                         'skutils'],
                        cwd=cwd)
    if p != 0:
        raise RuntimeError("Running cythonize failed!")

def configuration(parent_package="", top_path=None):
    # generate cython
    generate_cython()
    # config & setup
    config = Configuration(None, parent_package, top_path)
    config.add_subpackage("skutils")
    return config

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration().todict())