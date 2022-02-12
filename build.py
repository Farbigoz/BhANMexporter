from distutils.core import setup
from setuptools import setup
import Cython
from Cython.Distutils import Extension
from Cython.Build import cythonize

#setup(ext_modules=cythonize(r'core\utils\cpchecksum.pyx'))

# python build.py build_ext -i #--inplace

"""
ext_modules = cythonize(Extension(
        "ByteArray",
        sources=["core/anm/ByteArray.pxd"],
        language="c++",
))
"""

ext_modules = cythonize([
    Extension("raw", ["raw.pyx"],
              #libraries=['RawData'],
              #library_dirs=['.'],
              language="c++"),
    ])

setup(ext_modules=ext_modules)
