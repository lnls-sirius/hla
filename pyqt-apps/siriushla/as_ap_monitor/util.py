"""Util module."""

from siriuspy.diagsys.rfdiag.csdev import Const as RFDiagConst
from siriushla.as_ps_diag.util import \
    get_label2devices as get_pslabel2devices, \
    SEC2LABEL2SECPOS


def get_label2devices(sec):
    data = dict()
    data = get_pslabel2devices(sec).copy()
    if sec == 'LI':
        data['Egun'] = ['LI-01:EG-HVPS', 'LI-01:EG-FilaPS']
        data['RF'] = ['LI-01:RF-SHB', 'LI-01:RF-Kly-1', 'LI-01:RF-Kly-2']
        data['PU'] = ['LI-01:PU-Modltr-1', 'LI-01:PU-Modltr-2']
    elif sec == 'BO':
        data['RF'] = [RFDiagConst.BO_DEV, ]
    elif sec == 'SI':
        data['RF'] = [RFDiagConst.SIA_DEV, RFDiagConst.SIB_DEV]

    return data


def get_sec2dev_laypos(sec, label):
    SEC2LABEL2SECPOS['LI'].update({
        'Egun': (0, 3, 1, 1),
        'PU': (0, 4, 1, 1),
        'RF': (1, 3, 1, 1)})
    SEC2LABEL2SECPOS['BO'].update({
        'RF': (2, 1, 1, 1)})
    SEC2LABEL2SECPOS['SI'].update({
        'RF': (0, 8, 1, 1)})
    return SEC2LABEL2SECPOS[sec][label]
