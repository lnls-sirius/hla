"""Utilities."""

import qtawesome as qta
from siriushla.util import get_appropriate_color


def get_idff_icon(color=True):
    """Return IDFF icon."""
    color = get_appropriate_color('ID') if color else None
    icon = qta.icon(
        'fa5s.hammer', 'mdi.current-ac', 'mdi.current-ac', 'mdi.equal',
        options=[
            dict(scale_factor=0.3, color=color, offset=(-0.38, -0.01)),
            dict(scale_factor=0.3, color=color, offset=(-0.05, -0.01)),
            dict(scale_factor=0.3, color=color, offset=(0.15, -0.01)),
            dict(scale_factor=1.05, color=color, offset=(0.05, 0.0))])
    return icon
