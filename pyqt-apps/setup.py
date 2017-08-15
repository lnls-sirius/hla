#!/usr/bin/env python-sirius

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
    scripts=['scripts/sirius-hla-as-launcher.py',
	     'scripts/sirius-hla-as-ps-cycle.py',
	     'scripts/sirius-hla-bo-config-manager.py',
	     'scripts/sirius-hla-bo-ma-control.py',
	     'scripts/sirius-hla-si-config-manager.py',
	     'scripts/sirius-hla-si-ma-control.py',
	     'scripts/sirius-hla-tb-ma-control.py',
	     'scripts/sirius-hla-ts-ma-control.py',
	     'scripts/resources.py',
	    ],
    zip_safe=False
)
