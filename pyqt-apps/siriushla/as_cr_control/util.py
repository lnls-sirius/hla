from .screen_co import LABELS_CO, PVS_CO
from .screen_cbx1 import LABELS_CBX1, PVS_CBX1, LEDS_CBX1

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
    "Manifold Box": {
        "image": "cryo1",
        "labels": LABELS_CO,
        "pvs": PVS_CO
    }
}
