#!/usr/bin/env python3

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='siriushla',
    version=__version__,
    author='lnls-sirius',
    description='Client Applications for Sirius',
    url='https://github.com/lnls-sirius/hla/pyqt-apps',
    download_url='https://github.com/lnls-sirius/hla',
    license='GPL (version 3)',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['siriushla'],
    package_data={'siriushla': ['VERSION', '*/*.py']},
    # scripts=['scripts/*.py'],
    zip_safe=False
)
