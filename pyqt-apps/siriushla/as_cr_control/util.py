from .screen_co import LABELS_CO, PVS_CO
from .screen_cbx1 import LABELS_CBX1, PVS_CBX1, LEDS_CBX1
from .screen_cbx2 import LABELS_CBX2, PVS_CBX2, LEDS_CBX2
from .screen_manbox import LABELS_MANBOX, PVS_MANBOX

SCREENS = {
    "Co": {
        "image": "cryo1",
        "labels": LABELS_CO,
        "pvs": PVS_CO
    },
    "CBx 1": {
        "image": "cryo2",
        "labels": LABELS_CBX1,
        "pvs": PVS_CBX1,
        "leds": LEDS_CBX1
    },
    "CBx 2": {
        "image": "cryo2",
        "labels": LABELS_CBX2,
        "pvs": PVS_CBX2,
        "leds": LEDS_CBX2
    },
    "Manifold Box": {
        "image": "cryo3",
        "labels": LABELS_MANBOX,
        "pvs": PVS_MANBOX
    }
}
