#!/usr/bin/env python-sirius

"""PS detailed window."""

import sys
import argparse as _argparse
from siriuspy.search import PSSearch
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_control import PSDetailWindow
from siriushla.util import run_newprocess


parser = _argparse.ArgumentParser(
    description="Run Power Supply Detailed Control Interface.")
parser.add_argument("psname", type=str, help="PS name.")
args = parser.parse_args()

if PSSearch.conv_psname_2_psmodel(args.psname) == 'REGATRON_DCLink':
    run_newprocess(
        ['sirius-hla-as-ps-regatron-individual', '-dev', args.psname],
        is_pydm=True)
else:
    app = SiriusApplication()
    app.open_window(PSDetailWindow, parent=None, psname=args.psname)
    sys.exit(app.exec_())
