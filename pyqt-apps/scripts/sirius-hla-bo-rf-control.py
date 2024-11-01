#!/usr/bin/env python-sirius

"""BO RF Control Window."""

import argparse as _argparse
import sys

from siriushla.as_rf_control.advanced_details import ADCDACDetails, \
    AutoStartDetails, CalEqDetails, CalSysDetails, HardwareDetails, \
    LoopsDetails, RampsDetails, RFInputsDetails, TuningDetails
from siriushla.as_rf_control.control import RFMainControl
from siriushla.as_rf_control.details import CavityStatusDetails, FDLDetails, \
    LLRFInterlockDetails, SlowLoopErrorDetails, SlowLoopParametersDetails, \
    SSADetailsBO, TempMonitor, TransmLineStatusDetails
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX

parser = _argparse.ArgumentParser(
    description="Run RF Control Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
parser.add_argument('-d', "--detail", type=str, default='',
    help="Open a detail window defined by the parameter")
args = parser.parse_args()

windows = {
    'adcs-dacs': ADCDACDetails,
    'auto-start': AutoStartDetails,
    'cal-eq': CalEqDetails,
    'cal-sys': CalSysDetails,
    'hardware': HardwareDetails,
    'loops': LoopsDetails,
    'ramps': RampsDetails,
    'rf-inputs': RFInputsDetails,
    'tuning': TuningDetails,
    'fdl': FDLDetails,
    'cavity-status': CavityStatusDetails,
    'interlock': LLRFInterlockDetails,
    'sl-err': SlowLoopErrorDetails,
    'sl-param': SlowLoopParametersDetails,
    'temp-monitor': TempMonitor,
    'transm-line': TransmLineStatusDetails,
}

app = SiriusApplication()
if args.detail == '':
    app.open_window(RFMainControl, prefix=args.prefix, section='BO')
elif args.detail in windows.keys():
    app.open_window(windows[args.detail],
        prefix=args.prefix, section='BO')
elif args.detail == 'ssa':
    app.open_window(SSADetailsBO, prefix=args.prefix)
else:
    raise ValueError("Invalid detail argument.")

sys.exit(app.exec_())
