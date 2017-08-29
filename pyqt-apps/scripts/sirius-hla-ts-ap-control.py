#!/usr/bin/env python-sirius
"""High Level Application TS Control Window."""

import sys as _sys
import argparse as _argparse
from pydm.PyQt.QtCore import QFile as _QFile
from pydm import PyDMApplication as _PyDMApplication
import siriushla.resources
from siriushla.tl_ap_control.HLTLControl import TLAPControlWindow


if __name__ == '__main__':
    parser = _argparse.ArgumentParser(
                        description="Run TS Control HLA Interface.")
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

    window = TLAPControlWindow(prefix=args.prefix, tl='ts')
    window.show()
    _sys.exit(app.exec_())
