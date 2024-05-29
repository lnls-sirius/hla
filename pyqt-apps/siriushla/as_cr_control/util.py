from .screen_co import LABELS_CO, PVS_CO, HEADER_CO
from .screen_cbx1 import LABELS_CBX1, PVS_CBX1, LEDS_CBX1, HEADER_CBX
from .screen_cbx2 import LABELS_CBX2, PVS_CBX2, LEDS_CBX2
from .screen_manbox import LABELS_MANBOX, PVS_MANBOX, HEADER_MANBOX

SCREENS = {
    "Co": {
        "image": "cryo_co",
        "labels": LABELS_CO,
        "pvs": PVS_CO,
        "header": HEADER_CO
    },
    "CBx 1": {
        "image": "cryo_cbx1",
        "labels": LABELS_CBX1,
        "pvs": PVS_CBX1,
        "leds": LEDS_CBX1,
        "header": HEADER_CBX
    },
    "CBx 2": {
        "image": "cryo_cbx2",
        "labels": LABELS_CBX2,
        "pvs": PVS_CBX2,
        "leds": LEDS_CBX2,
        "header": HEADER_CBX
    },
    "Manifold Box": {
        "image": "cryo_manbox",
        "labels": LABELS_MANBOX,
        "pvs": PVS_MANBOX,
        "header": HEADER_MANBOX
    }
}