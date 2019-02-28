#!/usr/bin/env python-sirius
"""High Level Application to Booster Chromaticity Correction."""

import sys as _sys
import argparse as _argparse
from siriuspy.envars import vaca_prefix
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_opticscorr.HLOpticsCorr import OpticsCorrWindow


if __name__ == '__main__':
    parser = _argparse.ArgumentParser(
        description="Run Booster Chromaticity Correction HLA Interface.")
    parser.add_argument('-p', "--prefix", type=str, default=vaca_prefix,
                        help="Define the prefix for the PVs in the window.")
    args = parser.parse_args()

    app = SiriusApplication()

    window = OpticsCorrWindow(acc='bo', opticsparam='chrom',
                              prefix=args.prefix)
    window.show()
    _sys.exit(app.exec_())
