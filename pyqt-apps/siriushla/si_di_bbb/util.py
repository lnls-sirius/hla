"""BbB Util Module."""

from qtpy.QtGui import QColor, QPalette
import qtawesome as qta

from ..util import get_appropriate_color


def get_bbb_icon():
    """Get BbB icon."""
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
    """Set BbB color."""
    ncolor = '#b3e5ff' if device.endswith('H') \
        else '#ffb3b3' if device.endswith('V') \
        else '#f5f5f0'
    color = QColor(ncolor)
    pal = obj.palette()
    pal.setColor(QPalette.Background, color)
    obj.setAutoFillBackground(True)
    obj.setPalette(pal)
