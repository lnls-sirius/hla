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


with open('requirements.txt', 'r') as _f:
    _requirements = _f.read().strip().split('\n')


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
    install_requires=_requirements,
    package_data={
        'siriushla': ['VERSION', '*/*.py'],
        'siriushla.si_di_bbb': ['*.png', ],
        'siriushla.si_id_control': ['*.gif', ],
    },
    include_package_data=True,
    scripts=[
        'scripts/sirius-hla-as-ap-configdb.py',
        'scripts/sirius-hla-as-ap-cratemon.py',
        'scripts/sirius-hla-as-ap-effmon.py',
        'scripts/sirius-hla-as-ap-energybutton.py',
        'scripts/sirius-hla-as-ap-injection.py',
        'scripts/sirius-hla-as-ap-launcher.py',
        'scripts/sirius-hla-as-ap-macreport.py',
        'scripts/sirius-hla-as-ap-magoffconv.py',
        'scripts/sirius-hla-as-ap-monitor.py',
        'scripts/sirius-hla-as-ap-pvsconfigs.py',
        'scripts/sirius-hla-as-ap-pvsconfigs-save.py',
        'scripts/sirius-hla-as-ap-pvsconfigs-load.py',
        'scripts/sirius-hla-as-ap-radmon.py',
        'scripts/sirius-hla-as-di-bpm.py',
        'scripts/sirius-hla-as-di-dcct.py',
        'scripts/sirius-hla-as-di-scrn.py',
        'scripts/sirius-hla-as-ps-commands.py',
        'scripts/sirius-hla-as-ps-cycle.py',
        'scripts/sirius-hla-as-ps-detail.py',
        'scripts/sirius-hla-as-ps-diag.py',
        'scripts/sirius-hla-as-ps-graphmon.py',
        'scripts/sirius-hla-as-ps-monitor.py',
        'scripts/sirius-hla-as-pu-control.py',
        'scripts/sirius-hla-as-pu-detail.py',
        'scripts/sirius-hla-as-ti-afc.py',
        'scripts/sirius-hla-as-ti-control.py',
        'scripts/sirius-hla-as-ti-eve.py',
        'scripts/sirius-hla-as-ti-evg.py',
        'scripts/sirius-hla-as-ti-evr.py',
        'scripts/sirius-hla-as-ti-fout.py',
        'scripts/sirius-hla-bl-ap-imgproc.py',
        'scripts/sirius-hla-bo-ap-chargemon.py',
        'scripts/sirius-hla-bo-ap-chromcorr.py',
        'scripts/sirius-hla-bo-ap-injcontrol.py',
        'scripts/sirius-hla-bo-ap-ramp.py',
        'scripts/sirius-hla-bo-ap-sofb.py',
        'scripts/sirius-hla-bo-ap-tunecorr.py',
        'scripts/sirius-hla-bo-di-tune.py',
        'scripts/sirius-hla-bo-di-vlight.py',
        'scripts/sirius-hla-bo-offconfig.py',
        'scripts/sirius-hla-bo-ps-control.py',
        'scripts/sirius-hla-bo-ps-wfmerror.py',
        'scripts/sirius-hla-bo-pu-control.py',
        'scripts/sirius-hla-bo-rf-control.py',
        'scripts/sirius-hla-it-di-vlight.py',
        'scripts/sirius-hla-it-eg-control.py',
        'scripts/sirius-hla-it-ps-control.py',
        'scripts/sirius-hla-it-ti-control.py',
        'scripts/sirius-hla-li-ap-emittance.py',
        'scripts/sirius-hla-li-ap-energy.py',
        'scripts/sirius-hla-li-ap-mpscon.py',
        'scripts/sirius-hla-li-ap-mpsmon.py',
        'scripts/sirius-hla-li-di-bpms.py',
        'scripts/sirius-hla-li-di-scrns.py',
        'scripts/sirius-hla-li-eg-control.py',
        'scripts/sirius-hla-li-ps-control.py',
        'scripts/sirius-hla-li-pu-modltr.py',
        'scripts/sirius-hla-li-rf-llrf.py',
        'scripts/sirius-hla-li-va-control.py',
        'scripts/sirius-hla-si-ap-chromcorr.py',
        'scripts/sirius-hla-si-ap-currlt.py',
        'scripts/sirius-hla-si-ap-fofb.py',
        'scripts/sirius-hla-si-ap-genstatus.py',
        'scripts/sirius-hla-si-ap-idff.py',
        'scripts/sirius-hla-si-ap-orbintlk.py',
        'scripts/sirius-hla-si-ap-sofb.py',
        'scripts/sirius-hla-si-ap-tunecorr.py',
        'scripts/sirius-hla-si-di-bbb.py',
        'scripts/sirius-hla-si-di-scraps.py',
        'scripts/sirius-hla-si-di-tune.py',
        'scripts/sirius-hla-si-di-vlight.py',
        'scripts/sirius-hla-si-id-control.py',
        'scripts/sirius-hla-si-offconfig.py',
        'scripts/sirius-hla-si-ps-control.py',
        'scripts/sirius-hla-si-pu-control.py',
        'scripts/sirius-hla-si-rf-control.py',
        'scripts/sirius-hla-tb-ap-control.py',
        'scripts/sirius-hla-tb-ap-emittance.py',
        'scripts/sirius-hla-tb-ap-posang.py',
        'scripts/sirius-hla-tb-ap-sofb.py',
        'scripts/sirius-hla-tb-di-icts.py',
        'scripts/sirius-hla-tb-di-slits.py',
        'scripts/sirius-hla-tb-ps-control.py',
        'scripts/sirius-hla-tb-pu-control.py',
        'scripts/sirius-hla-ts-ap-control.py',
        'scripts/sirius-hla-ts-ap-posang.py',
        'scripts/sirius-hla-ts-ap-sofb.py',
        'scripts/sirius-hla-ts-di-icts.py',
        'scripts/sirius-hla-ts-ps-control.py',
        'scripts/sirius-hla-ts-pu-control.py',
        ],
    # test_suite='setup.my_test_suite',
    test_suite='setup.my_test_suite',
    zip_safe=False
    )
