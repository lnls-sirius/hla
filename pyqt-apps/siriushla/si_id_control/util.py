import qtawesome as qta
from siriushla.util import get_appropriate_color


def get_id_icon():
    color = get_appropriate_color('ID')
    icon = qta.icon('mdi.current-ac', 'mdi.current-ac', 'mdi.equal', options=[
        dict(scale_factor=0.48, color=color, offset=(-0.16, -0.01)),
        dict(scale_factor=0.48, color=color, offset=(0.16, -0.01)),
        dict(scale_factor=2.4, color=color, offset=(0.0, 0.0))])
    return icon
