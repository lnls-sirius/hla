#!/usr/bin/env python-sirius
"""High Level Application to Booster Chromaticity Correction."""

import sys as _sys
import argparse as _argparse
from siriushla.SiriusApplication import SiriusApplication
from siriushla import util as _util
from siriushla.as_ap_opticscorr.HLOpticsCorr import OpticsCorrWindow


if __name__ == '__main__':
    parser = _argparse.ArgumentParser(
        description="Run Storage Ring Chromaticity Correction HLA Interface.")
    parser.add_argument('-p', "--prefix", type=str, default='',
                        help="Define the prefix for the PVs in the window.")
    args = parser.parse_args()

    app = SiriusApplication()
    _util.set_style(app)

    window = OpticsCorrWindow(acc='si', opticsparam='chrom',
                              prefix=args.prefix)
    window.show()
    _sys.exit(app.exec_())
