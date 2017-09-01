#!/usr/bin/env python-sirius
"""High Level Application to Current and Lifetime Monitoring."""

import sys as _sys
import argparse as _argparse
from pydm.PyQt.QtCore import QFile as _QFile
from pydm import PyDMApplication as _PyDMApplication
import siriushla.resources
from siriushla.si_ap_currlt.HLCurrentLifetime import CurrLTWindow


if __name__ == '__main__':
    parser = _argparse.ArgumentParser(
                        description="Run Current and Lifetime HLA Interface.")
    parser.add_argument('-p', "--prefix", type=str, default='',
                        help="Define the prefix for the PVs in the window.")
    args = parser.parse_args()

    app = _PyDMApplication(None, _sys.argv)
    stream = _QFile(':/style.css')
    if stream.open(_QFile.ReadOnly):
        style = str(stream.readAll(), 'utf-8')
        stream.close()
    else:
        print(stream.errorString())
    app.setStyleSheet(style)

    window = CurrLTWindow(prefix=args.prefix)
    window.show()
    _sys.exit(app.exec_())
