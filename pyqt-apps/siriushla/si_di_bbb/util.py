"""BbB Util Module."""

import qtawesome as qta

from ..util import get_appropriate_color


def get_bbb_icon():
    """."""
    clr = get_appropriate_color('SI')
    icon = qta.icon(
        'fa5s.hammer', 'mdi.ellipse', 'mdi.ellipse', 'mdi.ellipse',
        options=[
            dict(
                scale_factor=0.4, offset=(-0.25, -0.20), color=clr,
                rotated=15),
            dict(scale_factor=0.3, offset=(-0.30, +0.20), color=clr),
            dict(scale_factor=0.3, offset=(+0.00, +0.07), color=clr),
            dict(scale_factor=0.3, offset=(+0.30, +0.20), color=clr),
        ])
    return icon


def set_bbb_color(obj, device):
    """."""
    if device.endswith('H'):
        obj.setStyleSheet('background-color:#b3e5ff')
    elif device.endswith('V'):
        obj.setStyleSheet('background-color:#ffb3b3')
    else:
        obj.setStyleSheet('background-color:#f5f5f0')
