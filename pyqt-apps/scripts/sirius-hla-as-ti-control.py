#!/usr/bin/env python-sirius

import sys
import argparse as _argparse
from PyQt5.QtCore import QFile
from pydm import PyDMApplication
import siriushla.resources
from siriushla.as_ti_control import main

parser = _argparse.ArgumentParser(description="Run Timing HLA Interface.")
parser.add_argument('-p', "--prefix", type=str, default='',
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = PyDMApplication(None, sys.argv)
stream = QFile(':/style.css')
if stream.open(QFile.ReadOnly):
    style = str(stream.readAll(), 'utf-8')
    stream.close()
else:
    print(stream.errorString())
app.setStyleSheet(style)

window = main(args.prefix)
window.show()
sys.exit(app.exec_())
