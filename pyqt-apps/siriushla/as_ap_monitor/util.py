"""Util module."""

from siriuspy.search import PSSearch
from siriushla.as_ps_diag.util import lips2filters, asps2filters, \
    bops2filters, sips2filters


def get_label2devices(sec):
    data = dict()
    if sec == 'LI':
        ps2filt = lips2filters
        data['Egun'] = ['LI-01:EG-HVPS', 'LI-01:EG-FilaPS']
        data['RF'] = ['LI-01:RF-Kly-1', 'LI-01:RF-Kly-2', 'LI-01:RF-SHB']
    elif sec == 'BO':
        ps2filt = bops2filters
        data['RF'] = ['BO-05D:RF-P5Cav', ]
    elif sec == 'SI':
        ps2filt = sips2filters
        data['RF'] = ['SI-02SB:RF-P7Cav', ]
    else:
        ps2filt = asps2filters

    for ps, filt in ps2filt.items():
        filt.update(sec=sec)
        data[ps] = PSSearch.get_psnames(filters=filt)
    return data
