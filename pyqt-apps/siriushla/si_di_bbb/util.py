"""BbB Util Module."""

import qtawesome as qta
from siriushla.util import get_appropriate_color


def get_bbb_icon():
    clr = get_appropriate_color('SI')
    icon = qta.icon(
        'fa5s.hammer', 'mdi.ellipse', 'mdi.ellipse', 'mdi.ellipse',
        options=[
            dict(scale_factor=0.4, offset=(-0.25, -0.20), color=clr,
                 rotated=15),
            dict(scale_factor=0.3, offset=(-0.30, +0.20), color=clr),
            dict(scale_factor=0.3, offset=(+0.00, +0.07), color=clr),
            dict(scale_factor=0.3, offset=(+0.30, +0.20), color=clr),
        ])
    return icon
