#-*- encoding: utf8 -*-
__author__ = 'flappy'

import os
import numpy
from numpy.distutils.misc_util import Configuration

def configuration(parent_package=None, top_path=None):
    config = Configuration("src", parent_package, top_path)
    libraries = []
    if os.name == 'posix':
        libraries.append('m')
    config.add_extension("memUtil",
                         sources=["memUtil.c"],
                         include_dirs=[numpy.get_include()],
                         libraries=libraries,
                         extra_compile_args=["-O3"])
    # config.add_subpackage("tests")
    config.set_options(ignore_setup_xxx_py=True,
                       assume_default_configuration=True,
                       delegate_options_to_subpackages=True,
                       quiet=True)
    return config

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration().todict())