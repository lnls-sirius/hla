from .colors import COLOR

LABELS_CBX1 = {
    "Compressor System": (
        [1, 58], [1, 78]),
    "1906\nAmbHtr": [7.75, 88],
    "Atm": (
        [10.75, 19], [87, 3]),
    "LN2": [19.75, 19],
    "Manual\nRegeneration Panel": [31.5, 23],
    "AE1.HP050": [41.25, 39],
    "Cbx2": [92, 3],
    "761\nCbx2": [92, 50],
    "1552\nCbx2": [92, 70],
    "1228\nCbx2": [92, 90],
    "NP1.100.U.TC": {
        "position": [15.25, 33.5],
        "shape": "side_arrows",
        "color": COLOR.dark_red
    },
    "HP1.EQ100": {
        "position": [17.5, 57.5],
        "shape": "line",
        "color": COLOR.transparent,
        "rotation": -90
    },
    "AE1.050.U.TC": {
        "position": [47.75, 46.6],
        "shape": "side_arrows",
        "color": COLOR.dark_red
    },
    "AS1.GQ015": {
        "position": [90.5, 8.25],
        "shape": "line",
        "color": COLOR.black
    },
    "AS1.QM011": {
        "position": [90.5, 15.5],
        "shape": "line",
        "color": COLOR.black
    },
    "AS1.GQ010": {
        "position": [90.5, 22],
        "shape": "line",
        "color": COLOR.black
    }
}

IHM_PREFIX = "dbAdsSta_strAdsA-"

PVS_CBX1 = {
    "GP1.HP1.010.P": {
        "position": [0.25, 62],
        "pvname": IHM_PREFIX + "m12GP1HP1010P",
        "color": COLOR.blue
    },
    "GP2.HP1.010.P": {
        "position": [6.75, 62],
        "pvname": IHM_PREFIX + "m12GP2HP1010P",
        "color": COLOR.blue
    },
    "CI1.LP1.015.P": {
        "position": [0.25, 69.5],
        "pvname": IHM_PREFIX + "m12CI1LP1015P",
        "color": COLOR.blue
    },
    "CI2.LP1.015.P": {
        "position": [6.75, 69.5],
        "pvname": IHM_PREFIX + "m12CI2LP1015P",
        "color": COLOR.blue
    },
    "NP1.110.T": {
        "position": [15.5, 24.5],
        "pvname": IHM_PREFIX + "m13CB1NP1110T",
        "color": COLOR.dark_red
    },
    "NP1.100.T": {
        "position": [15.5, 47.5],
        "pvname": IHM_PREFIX + "m13CB1NP1100T",
        "color": COLOR.dark_red
    },
    "NP1.QN010": {
        "position": [24, 39],
        "pvname": "m13CB1NP1QN010-rPrcOut",
        "color": COLOR.wine
    },
    "LP1.110.T": {
        "position": [20, 69.5],
        "pvname": IHM_PREFIX + "m13CB1LP1110T",
        "color": COLOR.dark_red
    },
    "AE1.QN020": {
        "position": [28.75, 47],
        "pvname": "m13CB1AE1QN020-rPrcOut",
        "color": COLOR.blue
    },
    "AE1.QN010": {
        "position": [28.75, 58.5],
        "pvname": "m13CB1AE1QN010-rPrcOut",
        "color": COLOR.blue
    },
    "AE1.035.T": {
        "position": [35.5, 39],
        "pvname": IHM_PREFIX + "m13CB1AE1035T",
        "color": COLOR.dark_red
    },
    "AE1.QN030": {
        "position": [37.25, 58.5],
        "pvname": "m13CB1AE1QN030-rPrcOut",
        "color": COLOR.blue
    },
    "AE1.065.T": {
        "position": [47.5, 39],
        "pvname": IHM_PREFIX + "m13CB1AE1065T",
        "color": COLOR.dark_red
    },
    "AE1.EB050": {
        "position": [41.75, 50],
        "pvname": "m13CB1AE1EB050-rPrcOut",
        "color": COLOR.black
    },
    "RU1.AE1.065.P": {
        "position": [57.5, 20.5],
        "pvname": IHM_PREFIX + "m13RU1AE1065P",
        "color": COLOR.blue
    },
    "AS1.020.P": {
        "position": [90.9, 26],
        "pvname": IHM_PREFIX + "m13VU1AS1020P",
        "color": COLOR.blue
    },
    "AE1.QN080": {
        "position": [80.5, 47],
        "pvname": "m13CB1AE1QN080-rPrcOut",
        "color": COLOR.blue
    }
}

LEDS_CBX1 = {
    "AE1.QN020.UPPER": {
        "position": [25.25, 39.8],
        "pvname": "AE1QN020UPPER"
    },
    "AE1.QN020.LOWER": {
        "position": [25.25, 42],
        "pvname": "AE1QN020LOWER"
    },
    "AE1.QN010.UPPER": {
        "position": [25.25, 51.25],
        "pvname": "AE1QN010UPPER"
    },
    "AE1.QN010.LOWER": {
        "position": [25.25, 53.6],
        "pvname": "AE1QN010LOWER"
    },
    "AE1.QN030": {
        "position": [32.25, 60],
        "pvname": "m13CB1AE1QN030-rPrcOut"
    },
    "AE1.QN080.UPPER": {
        "position": [77.3, 39.8],
        "pvname": "AE1QN080UPPER"
    },
    "AE1.QN080.LOWER": {
        "position": [77.3, 42],
        "pvname": "AE1QN080LOWER"
    }
}

HEADER_CBX = {
    "Coldmode": "m13CB1HP1QN410-iSta",
    "Warmup": "AlmSpareAi6-bStpCbWuOff",
    "Vaccum Cbx": "m13VU1AS1QM011-iSta",
    "Tu 1": "m13CB1TU1QN050-iSta",
    "Tu 2": "m13CB1TU2QN050-iSta",
    "Cbx LN2": "m13CB1NP1QN010-iSta",
    "Adsorber": "m13CB1AE1QN010-iSta",
    "Cold gas return": "m13CB1PR1QN510-iSta"
}
