#-*- encoding: utf8 -*-
__author__ = 'flappy'

import os
import sys
import subprocess
import numpy
from numpy.distutils.misc_util import Configuration



def configuration(parent_package="", top_path=None):
    # generate cython
    # config & setup
    config = Configuration("skutils", parent_package, top_path)
    config.add_subpackage("src")
    config.add_subpackage("tests")
    config.set_options(ignore_setup_xxx_py=True,
                       assume_default_configuration=True,
                       delegate_options_to_subpackages=True,
                       quiet=True)
    return config

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration().todict())