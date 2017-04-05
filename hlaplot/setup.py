#!/usr/bin/env python3

from setuptools import setup

with open('VERSION','r') as _f:
    __version__ = _f.read().strip()

setup(
    name='hlaplot',
    version=__version__,
    author='lnls-fac',
    description='LNLS HLA plot utilities',
    url='https://github.com/lnls-fac/hla/hlaplot',
    download_url='https://github.com/lnls-fac/hla',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['hlaplot'],
    package_data={'hlaplot': ['VERSION']},
    zip_safe=False,
)
