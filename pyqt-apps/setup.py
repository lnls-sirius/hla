#!/usr/bin/env python-sirius

"""HLA Setup."""

from setuptools import setup
import unittest

def my_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite


with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='siriushla',
    version=__version__,
    author='lnls-sirius',
    description='Client Applications for Sirius',
    url='https://github.com/lnls-sirius/hla/pyqt-apps',
    download_url='https://github.com/lnls-sirius/hla',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
        ],
    packages=['siriushla'],
    package_data={'siriushla': ['VERSION', '*/*.py']},
    scripts=[
        'sirius-hla-as-ap-pvsconfmgr.py',
        'sirius-hla-as-ap-servconf.py',
        'sirius-hla-as-di-bpm.py',
        'sirius-hla-as-ma-launcher.py',
        'sirius-hla-as-ps-cycle.py',
        'sirius-hla-as-ps-launcher.py',
        'sirius-hla-as-ti-control.py',
        'sirius-hla-bo-ap-chromcorr.py',
        'sirius-hla-bo-ap-currlt.py',
        'sirius-hla-bo-ap-ramp.py',
        'sirius-hla-bo-ap-sofb.py',
        'sirius-hla-bo-ap-tunecorr.py',
        'sirius-hla-bo-ma-control.py',
        'sirius-hla-bo-offconfig.py',
        'sirius-hla-si-ap-chromcorr.py',
        'sirius-hla-si-ap-currlt.py',
        'sirius-hla-si-ap-sofb.py',
        'sirius-hla-si-ap-tunecorr.py',
        'sirius-hla-si-ma-control.py',
        'sirius-hla-si-offconfig.py',
        'sirius-hla-si-ps-control.py',
        'sirius-hla-tb-ap-control.py',
        'sirius-hla-tb-ap-posang.py',
        'sirius-hla-tb-ap-sofb.py',
        'sirius-hla-tb-ma-control.py',
        'sirius-hla-ts-ap-control.py',
        'sirius-hla-ts-ap-posang.py',
        'sirius-hla-ts-ap-sofb.py',
        'sirius-hla-ts-ma-control.py',
        ],
    # test_suite='setup.my_test_suite',
    test_suite='setup.my_test_suite',
    zip_safe=False
    )
