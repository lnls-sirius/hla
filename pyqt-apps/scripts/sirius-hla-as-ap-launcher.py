#!/usr/bin/env python-sirius

"""Interface to handle main operation commands."""
import sys as _sys
import subprocess as _subprocess
import argparse as _argparse
from siriushla import util
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX
from siriushla.as_ap_launcher import MainLauncher


parser = _argparse.ArgumentParser(
    description="Run Operation Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
parser.add_argument(
    '-x', '--xpos', type=int, default=0,
    help="Define left origin point of window")
parser.add_argument(
    '-y', '--ypos', type=int, default=20,
    help="Define top origin point of window")
parser.add_argument(
    '-wi', '--width', type=int, default=0,
    help="Define window width value")
parser.add_argument(
    '-he', '--height', type=int, default=0,
    help="Define window height value")
args = parser.parse_args()

need_new_window = True
returnval = _subprocess.getoutput(
    'ps h -A -o pid,sess,command= | grep "[s]irius-hla-as-ap-launcher.py"')
if returnval:
    for info in returnval.split('\n'):
        pid, _, comm = info.split()[:3]
        window = util.check_window_by_pid(pid, comm)
        if window:
            need_new_window = False
            _subprocess.run(
                "wmctrl -iR " + window, stdin=_subprocess.PIPE, shell=True)
            break

if need_new_window:
    app = SiriusApplication()
    w = MainLauncher
    position = (args.xpos, args.ypos)
    if args.width and args.height != 0:
        size = (args.width, args.height)
    else:
        size = 'default'
    app.open_window(w, position=position, size=size, parent=None, prefix=args.prefix)
    scrn_size = app._get_desktop_geometry()
    print(scrn_size)
    _sys.exit(app.exec_())
