#!/usr/bin/env python-sirius

"""HLA Setup."""

from setuptools import setup, find_packages
import unittest


def my_test_suite():
    """."""
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
    packages=find_packages(),
    package_data={'siriushla': ['VERSION', '*/*.py']},
    include_package_data=True,
    scripts=[
        'scripts/sirius-hla-as-ap-energybutton.py',
        'scripts/sirius-hla-as-ap-injection.py',
        'scripts/sirius-hla-as-ap-magoffconv.py',
        'scripts/sirius-hla-as-ap-operation.py',
        'scripts/sirius-hla-as-ap-pvsconfmgr.py',
        'scripts/sirius-hla-as-ap-servconf.py',
        'scripts/sirius-hla-as-di-bpm.py',
        'scripts/sirius-hla-as-di-scrn.py',
        'scripts/sirius-hla-as-interlocks.py',
        'scripts/sirius-hla-as-launcher.py',
        'scripts/sirius-hla-as-ps-cycle.py',
        'scripts/sirius-hla-as-ps-detail.py',
        'scripts/sirius-hla-as-ps-diag.py',
        'scripts/sirius-hla-as-ps-monitor.py',
        'scripts/sirius-hla-as-ps-test.py',
        'scripts/sirius-hla-as-ti-control.py',
        'scripts/sirius-hla-bo-ap-chromcorr.py',
        'scripts/sirius-hla-bo-ap-currlt.py',
        'scripts/sirius-hla-bo-ap-ramp.py',
        'scripts/sirius-hla-bo-ap-sofb.py',
        'scripts/sirius-hla-bo-ap-tunecorr.py',
        'scripts/sirius-hla-bo-ma-control.py',
        'scripts/sirius-hla-bo-offconfig.py',
        'scripts/sirius-hla-bo-pm-control.py',
        'scripts/sirius-hla-bo-ps-control.py',
        'scripts/sirius-hla-li-launcher.py',
        'scripts/sirius-hla-si-ap-chromcorr.py',
        'scripts/sirius-hla-si-ap-currlt.py',
        'scripts/sirius-hla-si-ap-sofb.py',
        'scripts/sirius-hla-li-ap-emittance.py',
        'scripts/sirius-hla-li-ap-energy.py',
        'scripts/sirius-hla-si-ap-tunecorr.py',
        'scripts/sirius-hla-si-ma-control.py',
        'scripts/sirius-hla-si-offconfig.py',
        'scripts/sirius-hla-si-pm-control.py',
        'scripts/sirius-hla-si-ps-control.py',
        'scripts/sirius-hla-tb-ap-control.py',
        'scripts/sirius-hla-tb-ap-emittance.py',
        'scripts/sirius-hla-tb-ap-posang.py',
        'scripts/sirius-hla-tb-ap-sofb.py',
        'scripts/sirius-hla-tb-di-icts.py',
        'scripts/sirius-hla-tb-di-slits.py',
        'scripts/sirius-hla-tb-ma-control.py',
        'scripts/sirius-hla-tb-pm-control.py',
        'scripts/sirius-hla-tb-ps-control.py',
        'scripts/sirius-hla-ts-ap-control.py',
        'scripts/sirius-hla-ts-ap-posang.py',
        'scripts/sirius-hla-ts-ap-sofb.py',
        'scripts/sirius-hla-ts-di-icts.py',
        'scripts/sirius-hla-ts-ma-control.py',
        'scripts/sirius-hla-ts-pm-control.py',
        'scripts/sirius-hla-ts-ps-control.py',
        ],
    # test_suite='setup.my_test_suite',
    test_suite='setup.my_test_suite',
    zip_safe=False
    )
