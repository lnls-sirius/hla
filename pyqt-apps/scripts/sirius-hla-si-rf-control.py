#!/usr/bin/env python-sirius

"""SI RF Control Window."""

import argparse as _argparse
import sys

from siriuspy.envars import VACA_PREFIX

from siriushla.as_rf_control.advanced_details import ADCDACDetails, \
    AutoStartDetails, CalEqDetails, CalSysDetails, ConditioningDetails, \
    HardwareDetails, LoopsDetails, RampsDetails, RFInputsDetails, \
    TuningDetails
from siriushla.as_rf_control.control import RFMainControl
from siriushla.as_rf_control.details import CavityStatusDetails, FDLDetails, \
    LLRFInterlockDetails, SlowLoopErrorDetails, SlowLoopParametersDetails, \
    SSADetailsSI, TempMonitor, TransmLineStatusDetails
from siriushla.sirius_application import SiriusApplication

parser = _argparse.ArgumentParser(
    description="Run RF Control Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
parser.add_argument('-d', "--detail", type=str, default='',
    help="Open a detail window defined by the parameter")
parser.add_argument('-s', "--system", type=str, default='',
    help="Which system's detail window to open (A or B)")
parser.add_argument('-n', "--num_ssa", type=str, default='',
    help="SSA Tower's number. 1 or 2 for system A, 3 or 4 for system B")
args = parser.parse_args()

specific_system_windows = {
    'adcs-dacs': ADCDACDetails,
    'auto-start': AutoStartDetails,
    'cal-eq': CalEqDetails,
    'cal-sys': CalSysDetails,
    'conditioning': ConditioningDetails,
    'hardware': HardwareDetails,
    'loops': LoopsDetails,
    'ramps': RampsDetails,
    'rf-inputs': RFInputsDetails,
    'tuning': TuningDetails,
    'fdl': FDLDetails,
}

general_windows = {
    'cavity-status': CavityStatusDetails,
    'interlock': LLRFInterlockDetails,
    'sl-err': SlowLoopErrorDetails,
    'sl-param': SlowLoopParametersDetails,
    'temp-monitor': TempMonitor,
    'transm-line': TransmLineStatusDetails
}

app = SiriusApplication()
if args.detail == '':
    app.open_window(RFMainControl, prefix=args.prefix, section='SI')
elif args.detail in specific_system_windows.keys():
    if args.system != 'A' and args.system != 'B':
        raise ValueError("Invalid or missing system argument. Expected A or B")

    app.open_window(specific_system_windows[args.detail],
        prefix=args.prefix, section='SI', system=args.system)
elif args.detail in general_windows.keys():
    app.open_window(general_windows[args.detail],
        prefix=args.prefix, section='SI')
elif args.detail == 'ssa':
    if args.system != 'A' and args.system != 'B':
        raise ValueError("Invalid or missing system argument. Expected A or B.")
    elif args.system == 'A' and args.num_ssa not in ['1', '2']:
        raise ValueError("Invalid or missing num_ssa argument. Expected 1 or 2.")
    elif args.system == 'B' and args.num_ssa not in ['3', '4']:
        raise ValueError("Invalid or missing num_ssa argument. Expected 3 or 4.")

    app.open_window(SSADetailsSI, prefix=args.prefix, num=args.num_ssa,
        system=args.system)
else:
    raise ValueError("Invalid detail argument.")

sys.exit(app.exec_())
